from datetime import date

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import hash_key, new_license_key
from ..deps import audit, gestao, require_perfil
from ..models import Cliente, Licenca, Plano, Produto
from ..schemas import LicencaCriada, LicencaIn, LicencaOut, LicencaStatusIn, ProdutoOut

router = APIRouter(tags=["licenças"])
licencas_admin = require_perfil("suporte")


@router.get("/produtos", response_model=list[ProdutoOut])
def produtos(db: Session = Depends(get_db), _=Depends(gestao)):
    return db.scalars(select(Produto).order_by(Produto.nome)).all()


@router.get("/licencas", response_model=list[LicencaOut])
def listar(db: Session = Depends(get_db), _=Depends(gestao)):
    return db.scalars(select(Licenca).order_by(Licenca.criado_em.desc()).limit(500)).all()


@router.post("/licencas", response_model=LicencaCriada, status_code=201)
def criar(body: LicencaIn, request: Request, db: Session = Depends(get_db), admin=Depends(licencas_admin)):
    if not db.get(Cliente, body.cliente_id) or not db.get(Produto, body.produto_id):
        raise HTTPException(404, "Cliente ou produto não encontrado.")
    if body.plano_id and not db.get(Plano, body.plano_id):
        raise HTTPException(404, "Plano não encontrado.")
    chave = new_license_key()
    dados = body.model_dump()
    dados["inicio"] = dados["inicio"] or date.today()
    lic = Licenca(**dados, chave_hash=hash_key(chave))
    db.add(lic)
    db.flush()
    audit(db, admin, request, "licenca.criar", "licencas", lic.id, {"status": lic.status})
    db.commit()
    return LicencaCriada(**LicencaOut.model_validate(lic).model_dump(), chave=chave)


@router.patch("/licencas/{lic_id}/status", response_model=LicencaOut)
def mudar_status(lic_id: int, body: LicencaStatusIn, request: Request,
                 db: Session = Depends(get_db), admin=Depends(licencas_admin)):
    lic = db.get(Licenca, lic_id)
    if not lic:
        raise HTTPException(404, "Licença não encontrada.")
    antes, lic.status = lic.status, body.status
    audit(db, admin, request, "licenca.status", "licencas", lic.id, {"de": antes, "para": body.status})
    db.commit()
    return lic


@router.get("/licencas/validar", tags=["licenças (apps)"])
def validar(x_license_key: str = Header(...), db: Session = Depends(get_db)):
    """Chamado pelos apps (app_compras etc.) com a chave da instância. Sem login de admin."""
    lic = db.scalar(select(Licenca).where(Licenca.chave_hash == hash_key(x_license_key)))
    if not lic:
        raise HTTPException(404, "Licença não encontrada.")
    status = lic.status
    if status in ("trial", "ativa") and lic.fim and lic.fim < date.today():
        status = "expirada"
    produto, plano = db.get(Produto, lic.produto_id), db.get(Plano, lic.plano_id) if lic.plano_id else None
    return {
        "valida": status in ("trial", "ativa", "inadimplente"),
        "status": status,
        "somente_leitura": status == "inadimplente",
        "produto": produto.codigo if produto else None,
        "plano": plano.nome if plano else None,
        "limites": {"usuarios": lic.limite_usuarios or (plano.limite_usuarios if plano else None)},
        "modulos": lic.modulos or [],
        "validade_ate": lic.fim.isoformat() if lic.fim else None,
        "cache_segundos": 900,
    }
