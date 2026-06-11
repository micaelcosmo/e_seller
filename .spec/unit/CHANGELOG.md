# CHANGELOG — .spec/unit/

> Histórico específico da fase de unit specs.
> Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
> Datas no formato `AAAA-MM-DD`.

---

## [Não lançado]

### Adicionado — 2026-06-06
- `README.md`: índice e convenções da fase de unit specs.
- `_TEMPLATE-unit-spec.md`: template padrão de uma unit spec (orientada a TDD).
- `CHANGELOG.md`: este arquivo.
- Índices de área: `backend/`, `db/`, `security/`, `infra/`, `tests/`
  (catálogo das units planejadas em cada área).
- Exemplo preenchido: `backend/payments/service_process_webhook.md`.

### Decisões
- Granularidade **por componente**.
- Áreas: backend, db, security, infra, tests (separadas). **Frontend adiado**.
- Abordagem: estrutura + template + 1 exemplo → aprovação → geração de todas.

### Alterado — 2026-06-06 (padrões POO/SOLID)
- `_TEMPLATE-unit-spec.md` e `backend/payments/service_process_webhook.md`
  refatorados para **service = classe com injeção de dependência** no `__init__`,
  conforme [`../standards/`](../standards/). Renomeado o exemplo para `WebhookProcessor`.

### Adicionado — 2026-06-06 (lote da visão completa: +31 units)
- **RBAC:** `accounts/model_role`, `security/rbac_authorization`.
- **Catálogo estendido:** `catalog/model_author`, `model_publisher_series`, `model_tag`,
  `model_product_file`, `model_product_image`.
- **Reviews:** `model_review`, `service_review`, `router_reviews`.
- **Coupons:** `model_coupon`, `service_coupon`, `router_coupons`.
- **Wishlist:** `model_wishlist`, `service_wishlist`, `router_wishlist`.
- **Newsletter:** `model_subscriber`, `service_newsletter`, `router_newsletter`.
- **Cart:** `model_cart`, `service_cart`, `router_cart`.
- **Entitlement/Biblioteca:** `model_entitlement`, `service_grant_entitlement`, `router_library`.
- **Delivery/Payments:** `delivery/model_download_log`, `payments/model_refund`, `payments/service_refund`.
- **Billing/NF:** `billing/model_billing_profile`, `service_billing`, `router_billing`.
- `entitlement` resolve a posse única do e-book (UNIQUE user/product). Total ≈ 100 units.

### Adicionado — 2026-06-06 (trilha de testes aprofundada)
- `tests/`: guias `how_to_pytest`, `mocking_guide`, `security_testing`, `io_testing`;
  `CHANGELOG.md` próprio da pasta; README com **regra de manutenção contínua**.
- `CLAUDE.md` §2.2: trilha de testes marcada como viva (atualizar a cada tarefa).

### Adicionado — 2026-06-06 (geração de todas as units catalogadas)
- **~69 unit specs** geradas no formato aprovado (classe+DI; casos de teste TDD):
  - `backend/`: core (4), catalog (9), orders (6), payments (6), delivery (5),
    accounts (3), admin (4).
  - `db/`: alembic_setup, migration_initial, constraints, indexes, seeds (+ schema_overview).
  - `security/` (9), `infra/` (8), `tests/` (9).
- Índices de área marcados como ✅ gerados.
- **Pendente (lote futuro):** units dos domínios da visão completa (reviews, cupons,
  multi-autor/editora/série, wishlist/newsletter, RBAC, billing_profile).

### Adicionado — 2026-06-06 (desenho de DB)
- `db/schema_overview.md`: **desenho completo de entidades e relações** (ER em Mermaid),
  organizado por tiers (MVP / próximo / visão completa). Introduz `entitlement`,
  `order_item` (multi-item), multi-autor, cupons, reviews, etc. — visão de longo prazo
  que expande o `planning/10` (MVP).
- **Escopo do DB confirmado (2026-06-06):** reviews, cupons, multi-autor/editora/série,
  wishlist/newsletter, **RBAC completo** e **nota fiscal** (`billing_profile`) entram
  no objetivo final. Tiers passam a indicar ordem de implementação.

---

_Início da fase de unit specs: 2026-06-06_
