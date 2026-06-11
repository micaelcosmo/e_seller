# unit/backend/

Units do backend **FastAPI**, organizadas por **módulo de domínio** (ver
[`../../planning/08-arquitetura.md`](../../planning/08-arquitetura.md)).
Cada item abaixo será um arquivo `<tipo>_<nome>.md` no formato do
[`../_TEMPLATE-unit-spec.md`](../_TEMPLATE-unit-spec.md).

> ✅ **Todas as units deste índice foram geradas (2026-06-06).**
> Legenda de status: ⬜ a gerar · 🟦 exemplo pronto · ✅ gerada

## `core/`
- ⬜ `config.md` — settings via `pydantic-settings` (env vars).
- ⬜ `db_session.md` — engine SQLAlchemy + sessão por request.
- ⬜ `app_factory.md` — cria o app FastAPI, inclui routers, CORS, monta SQLAdmin.
- ⬜ `router_healthcheck.md` — `GET /api/healthz`.

## `catalog/`
- ⬜ `model_category.md`
- ⬜ `model_product.md`
- ⬜ `schema_category.md`
- ⬜ `schema_product.md` — `ProductOut`.
- ⬜ `service_list_products.md` — só `published`, paginado (RF-01).
- ⬜ `service_get_product.md` — detalhe por `slug` (RF-02).
- ⬜ `service_search_products.md` — busca por título/autor (RF-03).
- ⬜ `router_products.md` · ⬜ `router_categories.md`

## `orders/`
- ⬜ `model_order.md`
- ⬜ `schema_order.md` — `OrderCreateIn`, `OrderOut`.
- ⬜ `service_create_order.md` — cria `pending`, **congela preço** (RF-20,21).
- ⬜ `service_get_order.md` — status por `reference` (RF-25).
- ⬜ `service_state_machine.md` — transições válidas (RF-24, [`09`](../../planning/09-modelo-de-dominio.md)).
- ⬜ `router_orders.md`

## `payments/`
- ⬜ `model_payment.md` — `provider_payment_id` único (idempotência).
- ⬜ `gateway_mercadopago.md` — cliente externo (create preference / fetch payment).
- ⬜ `service_create_checkout.md` — gera `checkout_url` (RF-22).
- 🟦 `service_process_webhook.md` — **EXEMPLO PRONTO** (RF-23,24 / RNF-02,20).
- ⬜ `service_map_status.md` — status MP → estado do pedido.
- ⬜ `router_webhook.md` — `POST /api/webhooks/mercadopago`.

## `delivery/`
- ⬜ `model_download_grant.md`
- ⬜ `service_issue_download.md` — cria grant ao virar `paid` (RF-30).
- ⬜ `service_validate_grant.md` — expiração + limite (RF-31).
- ⬜ `service_stream_file.md` — stream sem expor path (RF-33).
- ⬜ `router_download.md` — `GET /api/download/{token}`.

## `accounts/`
- ⬜ `model_admin_user.md`
- ⬜ `service_authenticate.md` — valida credenciais (usa security/).
- ⬜ `router_auth.md` — `POST /api/auth/token` (RF-50).

## `admin/`
- ⬜ `sqladmin_setup.md` — montagem do SQLAdmin no app.
- ⬜ `admin_views_product.md` · ⬜ `admin_views_order.md` (RF-10..13, 40).
- ⬜ `admin_auth_backend.md` — login do painel.

> Notas: utilitários de **JWT, hash de senha, validação de assinatura e token de
> download** vivem em [`../security/`](../security/), referenciados por estas units.

---

## Visão completa (Tiers 🟡/🔵) — gerado 2026-06-06

### `catalog/` (extensões)
- ✅ `model_author.md` (Author + ProductAuthor) · ✅ `model_publisher_series.md`
- ✅ `model_tag.md` (Tag + ProductTag) · ✅ `model_product_file.md` · ✅ `model_product_image.md`

### `accounts/` + `security/` (RBAC)
- ✅ `accounts/model_role.md` (Role + UserRole) · ✅ `security/rbac_authorization.md` (`require_role`)

### `reviews/`
- ✅ `model_review.md` · ✅ `service_review.md` · ✅ `router_reviews.md`

### `coupons/`
- ✅ `model_coupon.md` (Coupon + CouponRedemption) · ✅ `service_coupon.md` · ✅ `router_coupons.md`

### `wishlist/`
- ✅ `model_wishlist.md` · ✅ `service_wishlist.md` · ✅ `router_wishlist.md`

### `newsletter/`
- ✅ `model_subscriber.md` · ✅ `service_newsletter.md` · ✅ `router_newsletter.md`

### `cart/`
- ✅ `model_cart.md` · ✅ `service_cart.md` · ✅ `router_cart.md`

### `entitlement/` (posse + Minha Biblioteca)
- ✅ `model_entitlement.md` · ✅ `service_grant_entitlement.md` · ✅ `router_library.md`

### `delivery/` + `payments/` (extensões)
- ✅ `delivery/model_download_log.md` · ✅ `payments/model_refund.md` · ✅ `payments/service_refund.md`

### `billing/` (NF)
- ✅ `model_billing_profile.md` · ✅ `service_billing.md` · ✅ `router_billing.md`

> Os schemas/routers de catálogo (`schema_product`, `router_products`) serão estendidos
> para expor autores/tags/imagens quando esses tiers forem implementados.
