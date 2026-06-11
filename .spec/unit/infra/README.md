# unit/infra/

Units de infraestrutura, derivadas de
[`../../planning/12-docker-e-ambientes.md`](../../planning/12-docker-e-ambientes.md) e
[`15-ci-cd.md`](../../planning/15-ci-cd.md).

> ✅ **Todas as units deste índice foram geradas (2026-06-06).**

- ✅ `ports.md` — **mapa de portas não-padrão** (base 48xxx), configuráveis por env.
- ⬜ `dockerfile_backend.md` — imagem do backend (Python 3.14-slim, deps, usuário não-root).
- ⬜ `docker_compose.md` — serviços `backend` + `db`, redes, `depends_on` + healthcheck.
- ⬜ `volumes.md` — `pgdata`, `ebook_files` (protegido), `media`.
- ⬜ `entrypoint.md` — espera o `db`, roda `alembic upgrade head`, sobe o servidor.
- ⬜ `env_config.md` — contrato do `.env.example` (chaves por ambiente).
- ⬜ `server_uvicorn_gunicorn.md` — Uvicorn (dev) / Gunicorn+Uvicorn workers (prod).
- ⬜ `ruff_config.md` — configuração do Ruff (lint + format) no `pyproject.toml`.
- ⬜ `ci_pipeline.md` — pipeline (ruff + pytest + cobertura), gates de merge.

> Frontend e seu container entram quando a tecnologia for decidida (ADR-005).
