#!/usr/bin/env bash
# Backup do banco PostgreSQL do e_seller.
# Uso: DATABASE_URL=postgresql://... BACKUP_DIR=/backups ./backup.sh
# Requer: pg_dump, gzip, variável DATABASE_URL.

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/app/data/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/e_seller_${TIMESTAMP}.dump.gz"

mkdir -p "${BACKUP_DIR}"

echo "[backup] Iniciando: ${BACKUP_FILE}"

# Converte URL async (postgresql+psycopg://...) para síntaxe pg_dump.
DB_URL="${DATABASE_URL/postgresql+psycopg:\/\//postgresql://}"
DB_URL="${DB_URL/sqlite+aiosqlite:\/\//}"

if [ -z "${DB_URL}" ]; then
  echo "[backup] ERRO: DATABASE_URL não definida." >&2
  exit 1
fi

pg_dump --format=custom "${DB_URL}" | gzip > "${BACKUP_FILE}"

echo "[backup] Concluído: ${BACKUP_FILE} ($(du -h "${BACKUP_FILE}" | cut -f1))"
