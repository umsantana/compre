import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from cryptography.fernet import Fernet

from .config import get_settings

_ph = PasswordHasher()
COOKIE_NAME = "compre_session"


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(hashed: str, password: str) -> bool:
    try:
        return _ph.verify(hashed, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def create_token(admin_id: int, perfil: str) -> str:
    s = get_settings()
    exp = datetime.now(timezone.utc) + timedelta(minutes=s.access_token_minutes)
    return jwt.encode({"sub": str(admin_id), "perfil": perfil, "exp": exp}, s.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])


# Chaves de licença: o texto puro é mostrado uma única vez; no banco fica só o hash.
def new_license_key() -> str:
    return "cmp_" + secrets.token_urlsafe(32)


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


# Credenciais das bases dos clientes (tabela instancias) ficam cifradas.
def encrypt(text: str) -> str:
    return Fernet(get_settings().fernet_key.encode()).encrypt(text.encode()).decode()


def decrypt(token: str) -> str:
    return Fernet(get_settings().fernet_key.encode()).decrypt(token.encode()).decode()
