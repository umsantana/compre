import os

os.environ["DATABASE_URL"] = "sqlite:///./test_compre.db"
os.environ["ENV"] = "local"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.db import Base, SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models import AdminUser, Produto  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        db.add(Produto(codigo="compras", nome="Compras"))
        db.add(AdminUser(nome="Admin", email="admin@teste.com", senha_hash=hash_password("senha-muito-longa-1"), perfil="super_admin"))
        db.commit()
    with TestClient(app) as c:
        yield c
