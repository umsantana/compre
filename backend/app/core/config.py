from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "local"  # local | hml | prod
    database_url: Optional[str] = None  # usado nos testes (sqlite)
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str = "compre_dev"
    db_user: str = ""
    db_password: str = ""
    secret_key: str = "troque-em-producao"
    fernet_key: str = ""
    cors_origins: str = "http://localhost:5173"
    cookie_secure: bool = False
    access_token_minutes: int = 60

    @property
    def docs_enabled(self) -> bool:
        return self.env != "prod"

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
