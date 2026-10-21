from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .core.db import get_db
from .core.security import COOKIE_NAME, decode_token
from .models import AdminUser, Auditoria

SAFE = ("GET", "HEAD", "OPTIONS")


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> AdminUser:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(401, "Sessão não iniciada.")
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise HTTPException(401, "Sessão expirada. Entre novamente.")
    admin = db.get(AdminUser, int(payload["sub"]))
    if not admin or not admin.ativo:
        raise HTTPException(401, "Usuário inativo.")
    # Proteção CSRF: cabeçalho customizado obrigatório em ações que alteram dados.
    # Sites de terceiros não conseguem enviá-lo (exigiria CORS liberado).
    if request.method not in SAFE and request.headers.get("x-requested-with") != "compre":
        raise HTTPException(403, "Requisição não autorizada.")
    return admin


def require_perfil(*perfis: str):
    def dep(admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
        if admin.perfil != "super_admin" and admin.perfil not in perfis:
            raise HTTPException(403, "Seu perfil não tem permissão para esta ação.")
        return admin

    return dep


gestao = require_perfil("comercial", "suporte")


def client_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


def audit(db: Session, admin: Optional[AdminUser], request: Request, acao: str,
          entidade: str, entidade_id: Optional[int] = None, detalhes: Optional[dict] = None) -> None:
    db.add(Auditoria(admin_id=admin.id if admin else None, acao=acao, entidade=entidade,
                     entidade_id=entidade_id, detalhes=detalhes, ip=client_ip(request)))
