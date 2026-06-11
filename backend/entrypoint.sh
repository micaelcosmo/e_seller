#!/bin/sh
# Aguarda o banco de dados aceitar conexões, depois sobe o servidor.
# Usado como CMD/ENTRYPOINT no Docker para garantir ordem de inicialização.
set -e

MAX_TRIES=30
TRIES=0

echo "Aguardando banco de dados..."
until python - <<'PYEOF' 2>/dev/null
import os, sys
try:
    import psycopg
    url = os.environ.get("DATABASE_URL", "")
    pg_url = url.replace("postgresql+psycopg://", "postgresql://")
    conn = psycopg.connect(pg_url, connect_timeout=3)
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PYEOF
do
  TRIES=$((TRIES + 1))
  if [ "$TRIES" -ge "$MAX_TRIES" ]; then
    echo "Banco nao respondeu apos $MAX_TRIES tentativas. Abortando."
    exit 1
  fi
  echo "  tentativa $TRIES/$MAX_TRIES — aguardando 2s..."
  sleep 2
done

echo "Banco de dados pronto. Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
