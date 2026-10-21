from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..deps import gestao
from ..models import Cliente, Lead, Licenca

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def resumo(db: Session = Depends(get_db), _=Depends(gestao)):
    contar = lambda col, tabela: dict(db.execute(select(col, func.count()).group_by(col)).all())  # noqa: E731
    return {
        "clientes_ativos": db.scalar(select(func.count()).select_from(Cliente).where(Cliente.status == "ativo")),
        "licencas_por_status": contar(Licenca.status, Licenca),
        "leads_por_status": contar(Lead.status, Lead),
    }
