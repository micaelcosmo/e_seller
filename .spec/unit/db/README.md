# unit/db/

Units de banco de dados (**PostgreSQL** + **SQLAlchemy/Alembic**), derivadas de
[`../../planning/10-modelo-de-dados.md`](../../planning/10-modelo-de-dados.md).

> ✅ **Todas as units deste índice foram geradas (2026-06-06).**

- 🟦 `schema_overview.md` — **desenho completo de entidades e relações (ER)**, em tiers
  (MVP / próximo / visão completa). Base para as units abaixo.
- 🟦 `uml-class-diagram.md` — **UML de classe (viva)** dos models; **atualizar a cada migração**.
- ⬜ `alembic_setup.md` — `alembic.ini`, `env.py`, integração com os models.
- ⬜ `migration_initial.md` — primeira migration: cria todas as tabelas.
- ⬜ `constraints.md` — UNIQUE (`provider_payment_id`, `token`, `slug`), CHECK (`price >= 0`, `amount >= 0`), FKs e `ON DELETE`.
- ⬜ `indexes.md` — índices de catálogo (`status`, `slug`) e busca (`reference`, `buyer_email`).
- ⬜ `seeds.md` — dados de exemplo para dev/test (3 produtos + 1 rascunho; pedidos em vários estados).

> As **definições dos models** (classes) ficam nas units de `backend/<módulo>/model_*.md`.
> Aqui tratamos do **schema físico, integridade e migrations**.

### Migrations dos tiers 🟡/🔵 (visão completa) — a detalhar por marco
- ⬜ `migration_tier_yellow.md` — author/product_author, tag/product_tag, product_file,
  product_image, review, coupon/coupon_redemption, cart/cart_item, entitlement,
  download_log, refund.
- ⬜ `migration_tier_blue.md` — role/user_role, publisher, series, wishlist/wishlist_item,
  newsletter_subscriber, billing_profile, refresh_token, audit_log.

> Cada migration adiciona constraints (ex.: UNIQUE `entitlement(user_id, product_id)`,
> UNIQUE `coupon.code`, UNIQUE `provider_refund_id`) e índices conforme as units.
