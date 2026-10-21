# Compre — gestão de clientes, licenças e planos

Painel administrativo (React) + API (FastAPI) + MySQL. Veja o plano completo no PDF de gestão.

## Rodar localmente (Windows)

**1. Banco** — rode `docs/database_setup.sql` no MySQL local (cria `compre_dev` e o usuário `compre_dev_app`).

**2. Backend** (`C:\Projetos\compre\backend`)
```
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        (edite: DB_PASSWORD, SECRET_KEY, FERNET_KEY)
alembic upgrade head          (cria as tabelas)
python -m app.scripts.seed    (cria os 3 produtos e o 1º administrador)
uvicorn app.main:app --reload
```
Documentação interativa da API: http://localhost:8000/api/docs (desligada em produção).
Testes: `pytest` (usam SQLite em arquivo temporário, não tocam no MySQL).

**3. Painel** (`C:\Projetos\compre\frontend`)
```
npm install
npm run dev                   (http://localhost:5173, já encaminha /api para a porta 8000)
```

## O que já existe (Fase 1)
Login admin (cookie httpOnly, bloqueio após 5 falhas, proteção CSRF), perfis, leads (endpoint público +
gestão), clientes, produtos, licenças (chave exibida uma vez, status), validação de licença para os apps
(`GET /api/licencas/validar` com o cabeçalho `X-License-Key`), auditoria e resumo.

## Próximas fases
2. Provisionamento de base zerada (tabela `instancias` já existe) · 3. Validação nos apps ·
4. Planos, assinaturas, faturas e gateway · 5. 2FA, monitoramento, LGPD · 6. Autoatendimento.

## Servidor (VPS)
Arquivos em `infra/`: Nginx (prod e hml), systemd e `scripts/deploy.sh`. Migrations: `alembic upgrade head`.
Nunca versione `.env`. Segredos ficam em `/etc/compre/<ambiente>.env` (permissão 600).
