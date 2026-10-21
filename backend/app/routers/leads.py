from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..deps import audit, gestao
from ..models import Lead
from ..schemas import LeadOut, LeadStatusIn

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=list[LeadOut])
def listar(status: Optional[str] = None, db: Session = Depends(get_db), _=Depends(gestao)):
    q = select(Lead).order_by(Lead.criado_em.desc()).limit(500)
    if status:
        q = q.where(Lead.status == status)
    return db.scalars(q).all()


@router.patch("/{lead_id}", response_model=LeadOut)
def mudar_status(lead_id: int, body: LeadStatusIn, request: Request,
                 db: Session = Depends(get_db), admin=Depends(gestao)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead não encontrado.")
    antes, lead.status = lead.status, body.status
    audit(db, admin, request, "lead.status", "leads", lead.id, {"de": antes, "para": body.status})
    db.commit()
    return lead
