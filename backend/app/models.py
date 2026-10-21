from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .core.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AdminUser(Base):
    __tablename__ = "admin_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(190), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[str] = mapped_column(String(20), default="suporte")  # super_admin|financeiro|suporte|comercial
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    totp_secret: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # 2FA (fase 5)
    falhas: Mapped[int] = mapped_column(Integer, default=0)
    bloqueado_ate: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ultimo_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Cliente(Base):
    __tablename__ = "clientes"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    documento: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)  # CPF/CNPJ
    email: Mapped[str] = mapped_column(String(190))
    telefone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ativo")  # ativo|inativo
    observacoes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Produto(Base):
    __tablename__ = "produtos"
    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True)  # compras|pontos_milhas|solicitacoes
    nome: Mapped[str] = mapped_column(String(100))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    template_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # tag Git do template


class Plano(Base):
    __tablename__ = "planos"
    id: Mapped[int] = mapped_column(primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    nome: Mapped[str] = mapped_column(String(100))
    periodicidade: Mapped[str] = mapped_column(String(20), default="mensal")
    preco: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    limite_usuarios: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    trial_dias: Mapped[int] = mapped_column(Integer, default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)


class Licenca(Base):
    __tablename__ = "licencas"
    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    plano_id: Mapped[Optional[int]] = mapped_column(ForeignKey("planos.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="trial")  # trial|ativa|inadimplente|suspensa|cancelada
    inicio: Mapped[date] = mapped_column(Date)
    fim: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    limite_usuarios: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    modulos: Mapped[list] = mapped_column(JSON, default=list)
    chave_hash: Mapped[str] = mapped_column(String(64), unique=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Instancia(Base):
    """Base de dados de um cliente para um produto (preenchida pelo provisionamento, fase 2)."""
    __tablename__ = "instancias"
    id: Mapped[int] = mapped_column(primary_key=True)
    licenca_id: Mapped[int] = mapped_column(ForeignKey("licencas.id"), unique=True)
    db_host: Mapped[str] = mapped_column(String(190))
    db_name: Mapped[str] = mapped_column(String(64))
    db_user: Mapped[str] = mapped_column(String(64))
    db_password_enc: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pendente")  # pendente|ativa|erro
    schema_version: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(190))
    telefone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    empresa: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    produto_interesse: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    mensagem: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="novo")  # novo|contato|trial|cliente|perdido
    utm_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_medium: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    consentimento_lgpd: Mapped[bool] = mapped_column(Boolean, default=False)
    consentimento_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Auditoria(Base):
    __tablename__ = "auditoria"
    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("admin_users.id"), nullable=True)
    acao: Mapped[str] = mapped_column(String(60))
    entidade: Mapped[str] = mapped_column(String(60))
    entidade_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    detalhes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
