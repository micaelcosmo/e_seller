# .spec/unit/

Fase de **especificação de unidades** do e_seller. Cada *unit spec* descreve um
**componente testável** (model, schema, service, router, gateway, migration…),
derivado dos pontos do [planning](../planning/). São a ponte direta para o **TDD**:
cada unit lista seus **casos de teste** (o "Red" que escrevemos antes do código).

> Metodologia em [`../../CLAUDE.md`](../../CLAUDE.md) (SDD + TDD + PEP 8).
> Nesta fase, **trabalhamos apenas em `.spec/unit/`**.

## Convenções

- **Granularidade:** uma unit = **um componente** (não um módulo inteiro).
- **Formato:** seguir [`_TEMPLATE-unit-spec.md`](_TEMPLATE-unit-spec.md).
- **Nomeação:** `<tipo>_<nome>.md` (ex.: `service_create_order.md`, `model_product.md`).
- **Áreas (pastas):** `backend/`, `db/`, `security/`, `infra/`, `tests/`.
  - `frontend/` **adiado** até a tecnologia ser decidida (ADR-005).
- Toda mudança registrada em [`CHANGELOG.md`](CHANGELOG.md).

## Áreas

| Pasta | Conteúdo | Índice |
|---|---|---|
| [`backend/`](backend/) | Units do FastAPI por módulo de domínio | [backend/README](backend/README.md) |
| [`db/`](db/) | Schema, constraints, migrations Alembic, seeds | [db/README](db/README.md) |
| [`security/`](security/) | Auth/JWT, webhook, token de download, LGPD | [security/README](security/README.md) |
| [`infra/`](infra/) | Docker, Compose, entrypoint, CI/CD | [infra/README](infra/README.md) |
| [`tests/`](tests/) | Units da infraestrutura de testes (fixtures, mocks, E2E) | [tests/README](tests/README.md) |

## Status desta fase

✅ **Units do MVP/próximo geradas (2026-06-06)** — ~69 unit specs.
✅ **Lote da visão completa gerado (2026-06-06)** — +31 units (RBAC, autores/editora/série,
tags, files/images, reviews, cupons, wishlist, newsletter, cart, entitlement,
download_log, billing, refund). **Total ≈ 100 unit specs.**

> Pendências técnicas residuais: migrations dos tiers 🟡/🔵 a detalhar por marco
> (ver [`db/README.md`](db/README.md)); estender `schema_product`/`router_products`
> para autores/tags/imagens quando implementados.
