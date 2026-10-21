#!/usr/bin/env bash
# Uso (na VPS):  ./deploy.sh hml develop      |      ./deploy.sh prod v0.1.0
# Pré-requisitos: usuário "compre", /opt/compre/<env>/venv criado, /etc/compre/<env>.env preenchido.
set -euo pipefail
ENV=${1:?uso: deploy.sh <hml|prod> <branch|tag>}; REF=${2:?informe a branch (hml) ou a tag (prod)}
REPO_URL=${REPO_URL:?defina REPO_URL (ex.: git@github.com:seu-usuario/compre.git)}
BASE=/opt/compre/$ENV; REL=$BASE/releases/$(date +%Y%m%d%H%M%S)
case $ENV in prod) DOMAIN=compre.amazonminas.com.br; SVC=compre-api; DB=compre;;
             hml)  DOMAIN=hml.compre.amazonminas.com.br; SVC=compre-hml-api; DB=compre_hml;; esac

git clone --depth 1 --branch "$REF" "$REPO_URL" "$REL"
(cd "$REL/frontend" && npm ci && npm run build)
(cd "$REL/backend"  && "$BASE/venv/bin/pip" install -q -r requirements.txt)

if [ "$ENV" = prod ]; then   # backup antes de alterar o esquema
  mkdir -p /backup && mysqldump --defaults-extra-file=/etc/compre/mysqldump.cnf --single-transaction "$DB" \
    | gzip > "/backup/pre_deploy_$(date +%Y%m%d%H%M%S).sql.gz"
fi

set -a; . "/etc/compre/$ENV.env"; set +a
(cd "$REL/backend" && "$BASE/venv/bin/alembic" upgrade head)

PREV=$(readlink "$BASE/current" || true)
ln -sfn "$REL" "$BASE/current"
sudo systemctl restart "$SVC"
sleep 3
if ! curl -fsS "https://$DOMAIN/api/health" >/dev/null; then
  echo "Health-check falhou: voltando para a versão anterior" >&2
  [ -n "$PREV" ] && ln -sfn "$PREV" "$BASE/current" && sudo systemctl restart "$SVC"
  exit 1
fi
ls -1dt "$BASE"/releases/* | tail -n +6 | xargs -r rm -rf   # mantém as 5 últimas versões
echo "Deploy de $REF em $ENV concluído."
