from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..deps import audit, gestao
from ..models import Cliente
from ..schemas import ClienteIn, ClienteOut

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=list[ClienteOut])
def listar(db: Session = Depends(get_db), _=Depends(gestao)):
    return db.scalars(select(Cliente).order_by(Cliente.nome)).all()


@router.post("", response_model=ClienteOut, status_code=201)
def criar(body: ClienteIn, request: Request, db: Session = Depends(get_db), admin=Depends(gestao)):
    cliente = Cliente(**body.model_dump())
    db.add(cliente)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Já existe um cliente com este documento.")
    audit(db, admin, request, "cliente.criar", "clientes", cliente.id)
    db.commit()
    return cliente


@router.get("/{cliente_id}", response_model=ClienteOut)
def obter(cliente_id: int, db: Session = Depends(get_db), _=Depends(gestao)):
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")
    return cliente


@router.put("/{cliente_id}", response_model=ClienteOut)
def atualizar(cliente_id: int, body: ClienteIn, request: Request,
              db: Session = Depends(get_db), admin=Depends(gestao)):
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")
    for k, v in body.model_dump().items():
        setattr(cliente, k, v)
    audit(db, admin, request, "cliente.atualizar", "clientes", cliente.id)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Já existe um cliente com este documento.")
    return cliente
