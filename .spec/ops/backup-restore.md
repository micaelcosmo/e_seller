# Runbook: Backup e Restore (PostgreSQL)

> Trilha ops · e_seller · 2026-06-10

---

## Por que importa

Perda do banco = perda de pedidos, pagamentos e posse (entitlements). Backup é
obrigatório desde o início (ver risco R-21 em
[`../planning/22-matriz-de-riscos.md`](../planning/22-matriz-de-riscos.md)).

---

## Backup — via Docker Compose

Script em `backend/scripts/backup.sh`. Executar dentro do container de banco
ou de um container auxiliar com acesso ao volume `pgdata`:

```bash
# Opção 1: exec no container do backend (tem psycopg; não tem pg_dump)
# Opção 2: container auxiliar com pg_dump
docker run --rm \
  --network e_seller_default \
  -e DATABASE_URL="${DATABASE_URL}" \
  -v "$(pwd)/backups:/backups" \
  postgres:16-alpine \
  pg_dump --format=custom "${DATABASE_URL}" | \
  gzip > "/backups/e_seller_$(date +%Y%m%d_%H%M%S).dump.gz"
```

**Frequência recomendada:** diário (via cron do host ou serviço separado).

**Retenção:** mínimo 30 dias; LGPD aplica — backups com dados pessoais devem
seguir a mesma política de retenção da base principal.

---

## Restore

```bash
# 1. Parar o backend para evitar escrita durante o restore.
docker compose stop backend

# 2. Descomprimir e restaurar.
gunzip < backup_20260610_120000.dump.gz | \
  docker exec -i e_seller-db-1 \
  pg_restore -d e_seller -c -U e_seller

# 3. Subir o backend.
docker compose start backend

# 4. Verificar revisão do Alembic e healthcheck.
docker exec e_seller-backend-1 alembic current
curl http://localhost:48080/api/v1/healthz
```

---

## Arquivos de e-book (volume `ebook_files`)

O volume `ebook_files` (montado em `/app/storage/ebooks`) **não está no Postgres**
e precisa de backup separado:

```bash
# Tar do volume via container auxiliar.
docker run --rm \
  -v e_seller_ebook_files:/source:ro \
  -v "$(pwd)/backups:/backups" \
  alpine \
  tar -czf "/backups/ebooks_$(date +%Y%m%d).tar.gz" -C /source .
```

---

## Drill (teste de restauração)

Periodicamente, restaurar em ambiente isolado (ex.: `docker compose -p test ...`)
e validar:

1. Produtos visíveis no catálogo.
2. Login admin funciona.
3. Healthcheck retorna 200.

**Backup não testado ≈ sem backup.**

---

## Changelog

- **2026-06-10**: Comandos Docker concretos adicionados; backup script criado em `backend/scripts/backup.sh`.
