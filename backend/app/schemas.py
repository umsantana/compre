from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Perfil = Literal["super_admin", "financeiro", "suporte", "comercial"]
LeadStatus = Literal["novo", "contato", "trial", "cliente", "perdido"]
LicencaStatus = Literal["trial", "ativa", "inadimplente", "suspensa", "cancelada"]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LoginIn(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=200)


class AdminOut(ORM):
    id: int
    nome: str
    email: str
    perfil: str


class LeadIn(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    email: EmailStr
    telefone: Optional[str] = Field(default=None, max_length=30)
    empresa: Optional[str] = Field(default=None, max_length=150)
    produto_interesse: Optional[str] = Field(default=None, max_length=40)
    mensagem: Optional[str] = Field(default=None, max_length=2000)
    utm_source: Optional[str] = Field(default=None, max_length=100)
    utm_medium: Optional[str] = Field(default=None, max_length=100)
    utm_campaign: Optional[str] = Field(default=None, max_length=100)
    consentimento_lgpd: bool
    website: Optional[str] = None  # honeypot: humanos não preenchem

    @field_validator("consentimento_lgpd")
    @classmethod
    def exige_consentimento(cls, v: bool) -> bool:
        if not v:
            raise ValueError("É necessário aceitar o tratamento dos dados para enviar.")
        return v


class LeadOut(ORM):
    id: int
    nome: str
    email: str
    telefone: Optional[str]
    empresa: Optional[str]
    produto_interesse: Optional[str]
    mensagem: Optional[str]
    status: str
    utm_source: Optional[str]
    utm_campaign: Optional[str]
    criado_em: datetime


class LeadStatusIn(BaseModel):
    status: LeadStatus


class ClienteIn(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    documento: Optional[str] = Field(default=None, max_length=20)
    email: EmailStr
    telefone: Optional[str] = Field(default=None, max_length=30)
    status: Literal["ativo", "inativo"] = "ativo"
    observacoes: Optional[str] = None


class ClienteOut(ClienteIn, ORM):
    id: int
    criado_em: datetime


class ProdutoOut(ORM):
    id: int
    codigo: str
    nome: str
    ativo: bool


class LicencaIn(BaseModel):
    cliente_id: int
    produto_id: int
    plano_id: Optional[int] = None
    status: LicencaStatus = "trial"
    inicio: Optional[date] = None
    fim: Optional[date] = None
    limite_usuarios: Optional[int] = Field(default=None, ge=1)
    modulos: list[str] = []


class LicencaOut(ORM):
    id: int
    cliente_id: int
    produto_id: int
    plano_id: Optional[int]
    status: str
    inicio: date
    fim: Optional[date]
    limite_usuarios: Optional[int]
    modulos: list
    criado_em: datetime


class LicencaCriada(LicencaOut):
    chave: str  # exibida somente na criação


class LicencaStatusIn(BaseModel):
    status: LicencaStatus
