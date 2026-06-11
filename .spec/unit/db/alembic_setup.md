# Unit: alembic_setup (`migration`/config)

> Tipo: `migration` (config) · Área: `db`
> Deriva de: ADR-002 ([`planning/07`](../../planning/07-adr-stack.md)), [`planning/12`](../../planning/12-docker-e-ambientes.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Configurar o Alembic integrado aos models SQLAlchemy, para gerar/aplicar migrations.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/alembic.ini`, `backend/alembic/env.py` |
| Teste | `backend/tests/db/test_alembic_setup.py` |

## 3. Contrato (config)

- `env.py` importa o `Base.metadata` (todos os models registrados).
- `sqlalchemy.url` vem de `Settings.database_url` (não hardcoded).
- `target_metadata = Base.metadata` para autogeneration.

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/config` | URL do banco |
| `core/db_session` (Base) | metadata |
| todos os `model_*` | estarem importados antes do autogenerate |

## 5. Comportamento / regras

- `alembic revision --autogenerate` enxerga **todos** os models.
- `alembic upgrade head` roda no `entrypoint` ([`infra/entrypoint`](../infra/README.md)).
- Migrations versionadas no Git.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | `upgrade head` em DB limpo | cria todas as tabelas |
| T2 | `downgrade`/`upgrade` | reversível sem erro |
| T3 | autogenerate sem mudanças | não gera migration vazia inesperada |

## 7. Rastreabilidade

- ADR-002 · Units: `migration_initial`, `core/config`, `infra/entrypoint`

## 8. Pendências

- [ ] Nomeação/numeração das revisions (convention).
