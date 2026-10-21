from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..deps import client_ip
from ..models import Lead, utcnow
from ..schemas import LeadIn

router = APIRouter(prefix="/public", tags=["público"])


@router.post("/leads", status_code=201)
def criar_lead(body: LeadIn, request: Request, db: Session = Depends(get_db)):
    if body.website:  # honeypot preenchido = robô; responde sucesso sem gravar
        return {"ok": True}
    data = body.model_dump(exclude={"website"})
    data["email"] = data["email"].lower()
    db.add(Lead(**data, consentimento_em=utcnow(), ip=client_ip(request)))
    db.commit()
    return {"ok": True}
