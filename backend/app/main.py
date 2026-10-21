from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .routers import auth, clientes, dashboard, health, leads, licencas, public


def create_app() -> FastAPI:
    s = get_settings()
    if s.env != "local" and (s.secret_key.startswith("troque") or len(s.secret_key) < 32):
        raise RuntimeError("Defina SECRET_KEY (mínimo 32 caracteres) no arquivo de ambiente de hml/prod.")
    app = FastAPI(
        title="Compre API",
        docs_url="/api/docs" if s.docs_enabled else None,  # desligado em produção
        redoc_url=None,
        openapi_url="/api/openapi.json" if s.docs_enabled else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=s.cors_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "X-Requested-With", "X-License-Key"],
    )
    for r in (health.router, auth.router, public.router, leads.router, clientes.router,
              licencas.router, dashboard.router):
        app.include_router(r, prefix="/api")
    return app


app = create_app()
