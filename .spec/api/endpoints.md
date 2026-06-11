# Catálogo de Endpoints (contrato)

> Trilha API · e_seller · 2026-06-06 · prefixo base `/api/v1`
> Consolida o contrato; detalhe de cada um nas units `router_*`.

---

## Público

| Método | Rota | Resumo | Unit |
|---|---|---|---|
| GET | `/products` | Lista publicados (paginado, `q` opcional) | `catalog/router_products` |
| GET | `/products/{slug}` | Detalhe do produto | `catalog/router_products` |
| GET | `/categories` | Lista categorias | `catalog/router_categories` |
| POST | `/orders` | Cria pedido + checkout | `orders/router_orders` |
| GET | `/orders/{reference}` | Status do pedido | `orders/router_orders` |
| GET | `/download/{token}` | Download (grant válido) | `delivery/router_download` |

## Webhook (terceiro)

| Método | Rota | Resumo | Unit |
|---|---|---|---|
| POST | `/webhooks/mercadopago` | Notificação de pagamento (idempotente) | `payments/router_webhook` |

## Autenticação / Admin

| Método | Rota | Resumo | Unit |
|---|---|---|---|
| POST | `/auth/token` | Login (OAuth2) → JWT | `accounts/router_auth` |
| — | `/admin` | Painel SQLAdmin (sessão) | `admin/sqladmin_setup` |

## Saúde

| Método | Rota | Resumo | Unit |
|---|---|---|---|
| GET | `/healthz` | Healthcheck | `core/router_healthcheck` |

> Schemas de entrada/saída: ver as units `schema_*` correspondentes. Endpoints da
> **visão completa** (reviews, wishlist, cupons, biblioteca/entitlements) serão
> adicionados aqui quando suas units forem geradas.
