# Storefront (loja)

> Trilha frontend · e_seller · 2026-06-07 · Status: **Rascunho**
> Consome a API `/api/v1` ([`../api/endpoints.md`](../api/endpoints.md)).

---

## 1. Páginas (rotas)

| Rota | Página | API consumida |
|---|---|---|
| `/` | **Home / landing** (destaques + chamada para o catálogo) | `GET /products` |
| `/catalogo` | Catálogo completo | `GET /products` |
| `/ebooks/[slug]` | Detalhe do e-book (SSR/SEO) | `GET /products/{slug}` |
| `/buscar` | Resultados de busca | `GET /products?q=` |
| `/login` · `/cadastro` | **Login / cadastro do comprador** | `POST /auth/token` · `POST /auth/register` |
| `/checkout/[reference]` | Acompanhamento do pedido | `GET /orders/{reference}` |
| `/minha-biblioteca` | "Minha Biblioteca" (posses) | `GET /library` (autenticado) |
| `/conta` | Conta do comprador (dados, histórico) | `GET /orders` (autenticado) |

> **Home/landing** é a porta de entrada (não o catálogo cru). **Login do comprador** é
> **opcional**: dá acesso a biblioteca/wishlist/histórico e melhora a navegação, mas a
> **compra como convidado** (só e-mail) continua possível. Login admin é à parte (JWT).

## 2. Fluxo de compra (frente)

```
catálogo → detalhe → "Comprar" (e-mail) → POST /orders → redirect checkout_url (Mercado Pago)
   → retorno → tela de status (faz polling em GET /orders/{reference})
   → quando "paid": exibe acesso ao download / link da biblioteca
```

> O download **só** aparece após o status do pedido virar `paid` (confirmado pelo
> webhook no backend) — o frontend nunca decide isso sozinho (RNF-01).

## 3. Componentes principais

- `ProductCard`, `ProductDetail`, `SearchBar`, `BuyButton`, `OrderStatus`,
  `LibraryList`, `AuthForm`.
- Componentes funcionais (React) com tipos do OpenAPI.

## 4. Integração com a API

- Client gerado a partir do **OpenAPI** (tipos sempre em dia com o backend).
- Base URL por env (`NEXT_PUBLIC_API_BASE`), apontando para `http://localhost:48080/api/v1`
  em dev (ver [`../unit/infra/ports.md`](../unit/infra/ports.md)) ou o domínio do túnel
  ([`../distribution/`](../distribution/)).
- Tratamento de erros conforme [`../api/errors.md`](../api/errors.md) (422/404/401…).

## 5. Acessibilidade & responsivo

- Responsivo (desktop/mobile) — RNF-50; acessível (semântica, contraste).

## 6. Pendências

- [ ] Biblioteca de estilo (Tailwind?); design system mínimo.
- [ ] Carrinho (Tier 🟡) e cupom no checkout.
- [ ] i18n (pt-BR fixo por enquanto).
