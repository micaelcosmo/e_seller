# Runbook: Deploy

> Trilha ops · e_seller · 2026-06-06 · Status: **Rascunho**

---

## Pré-requisitos

- Branch `main` verde no CI (Ruff + testes + cobertura).
- Imagem Docker do backend buildada e versionada (tag por commit/tag).
- Segredos de produção disponíveis no cofre (não `.env`).

## Passos

1. **Tag/release** da versão a publicar.
2. **Build** da imagem de produção (Dockerfile do backend).
3. **Migrations:** o `entrypoint.sh` roda `alembic upgrade head` na subida
   (ver [`../unit/infra/entrypoint.md`](../unit/infra/entrypoint.md)).
4. **Subir** o serviço (Gunicorn + Uvicorn workers).
5. **Verificar:** `GET /api/v1/healthz` → `200`; `/docs` conforme política de ambiente.
6. **Smoke test:** fluxo mínimo (catálogo responde; webhook sandbox/healthy).

## Rollback

- Reapontar para a imagem da versão anterior.
- **Cuidado com migrations destrutivas:** preferir migrations compatíveis para trás
  (expand/contract). Se necessário, `alembic downgrade <rev>` testado antes.

## Verificação pós-deploy

- [ ] Healthcheck OK.
- [ ] Logs sem erros de inicialização.
- [ ] Pagamento de teste (sandbox) confirma e libera download.

## Pendências

- [ ] Destino de hospedagem de baixo custo (definir).
- [ ] Automação de CD (hoje manual — ver [`../planning/15-ci-cd.md`](../planning/15-ci-cd.md)).
