from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..core.db import get_db
from ..core.security import COOKIE_NAME, create_token, verify_password
from ..deps import audit, get_current_admin
from ..models import AdminUser, utcnow
from ..schemas import AdminOut, LoginIn

router = APIRouter(prefix="/auth", tags=["auth"])
MAX_FALHAS, BLOQUEIO_MIN = 5, 15


@router.post("/login", response_model=AdminOut)
def login(body: LoginIn, request: Request, response: Response, db: Session = Depends(get_db)):
    s = get_settings()
    now = utcnow()
    admin = db.scalar(select(AdminUser).where(AdminUser.email == body.email.lower()))
    if admin and admin.bloqueado_ate and admin.bloqueado_ate > now:
        raise HTTPException(429, "Muitas tentativas. Aguarde alguns minutos e tente de novo.")
    if not admin or not admin.ativo or not verify_password(admin.senha_hash, body.senha):
        if admin:
            admin.falhas += 1
            if admin.falhas >= MAX_FALHAS:
                admin.bloqueado_ate = now + timedelta(minutes=BLOQUEIO_MIN)
                admin.falhas = 0
            db.commit()
        raise HTTPException(401, "E-mail ou senha incorretos.")
    admin.falhas, admin.bloqueado_ate, admin.ultimo_login = 0, None, now
    audit(db, admin, request, "login", "admin_users", admin.id)
    db.commit()
    response.set_cookie(
        COOKIE_NAME, create_token(admin.id, admin.perfil), httponly=True, secure=s.cookie_secure,
        samesite="lax", max_age=s.access_token_minutes * 60, path="/",
    )
    return admin


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/me", response_model=AdminOut)
def me(admin: AdminUser = Depends(get_current_admin)):
    return admin
