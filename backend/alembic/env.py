from alembic import context

import app.models  # noqa: F401  (registra as tabelas no metadata)
from app.core.db import Base, engine

target_metadata = Base.metadata


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise SystemExit("Modo offline não suportado; rode com acesso ao banco.")
run_migrations_online()
