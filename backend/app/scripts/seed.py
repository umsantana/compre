"""Cria os 3 produtos e o primeiro administrador.  Uso: python -m app.scripts.seed"""
import getpass
import os

from sqlalchemy import select

from ..core.db import SessionLocal
from ..core.security import hash_password
from ..models import AdminUser, Produto

PRODUTOS = [("compras", "Compras"), ("pontos_milhas", "Pontos e Milhas"), ("solicitacoes", "Solicitações")]


def main() -> None:
    with SessionLocal() as db:
        for codigo, nome in PRODUTOS:
            if not db.scalar(select(Produto).where(Produto.codigo == codigo)):
                db.add(Produto(codigo=codigo, nome=nome))
        email = (os.getenv("ADMIN_EMAIL") or input("E-mail do administrador: ")).strip().lower()
        if db.scalar(select(AdminUser).where(AdminUser.email == email)):
            print("Administrador já existe; nada a fazer.")
        else:
            senha = os.getenv("ADMIN_PASSWORD") or getpass.getpass("Senha (mín. 12 caracteres): ")
            if len(senha) < 12:
                raise SystemExit("Senha curta demais.")
            db.add(AdminUser(nome="Administrador", email=email, senha_hash=hash_password(senha), perfil="super_admin"))
            print("Administrador criado.")
        db.commit()
    print("Seed concluído.")


if __name__ == "__main__":
    main()
