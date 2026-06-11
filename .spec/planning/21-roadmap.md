# 21 — Roadmap

> Documento de planning · e_seller · 2026-06-06
> Sequência de entrega por marcos. Cada marco respeita SDD + TDD e a DoD ([`16`](16-definition-of-done.md)).

---

## Visão geral

```
M0 Fundação  →  M1 Domínio+Admin  →  M2 Catálogo  →  M3 Pedido+Checkout
   →  M4 Webhook+Estados  →  M5 Entrega segura  →  MVP ✅  →  M6+ Evoluções
```

---

## M0 — Fundação (esqueleto)
**Objetivo:** ambiente roda do zero via Docker.
- Estrutura do projeto **FastAPI** (`app/` com módulos: `core`, etc.) + Uvicorn.
- SQLAlchemy + **Alembic** configurados (engine, sessão, base, primeira migration vazia).
- `docker-compose` com `backend` + `db` (Postgres).
- `entrypoint.sh` (`alembic upgrade head` + start), `GET /api/healthz`, `/docs` ativo.
- Ruff + pytest (+ httpx) configurados; CI inicial verde.
- **Saída:** `docker compose up` sobe e `/api/healthz` responde; pipeline verde.

## M1 — Domínio + Admin
**Objetivo:** modelar e administrar produtos/pedidos.
- Models SQLAlchemy: `Product`, `Category`, `Order`, `Payment`, `DownloadGrant` + migration Alembic.
- **Painel SQLAdmin** para CRUD de produto e visualização de pedidos (RF-10..13, 40).
- Autenticação de admin (JWT) básica (RF-50).
- Testes das invariantes e da máquina de estados.
- **Saída:** admin publica e-book; estados de pedido testados.

## M2 — Catálogo via API
**Objetivo:** vitrine consumível pelo frontend.
- Endpoints `GET /api/products` (RF-01) e `GET /api/products/{slug}` (RF-02); só `published`.
- Busca simples (RF-03) — se couber.
- Schemas Pydantic (`ProductOut`); contrato visível em `/docs`.
- Testes US-01, US-02.
- **Saída:** API de catálogo navegável e documentada.

## M3 — Pedido + Checkout
**Objetivo:** iniciar compra e ir ao pagamento.
- `create_order` (preço congelado), `POST /comprar/<slug>/` (RF-20,21).
- Integração de checkout Mercado Pago **sandbox** (RF-22), cliente isolado/mockável.
- Testes US-04.
- **Saída:** compra cria pedido `pending` e redireciona ao checkout.

## M4 — Webhook + Máquina de estados
**Objetivo:** confirmar pagamento com segurança.
- `POST /webhooks/mercadopago/` com validação + idempotência (RF-23,24 / RNF-02,20).
- Transições de estado e mapeamento de status.
- Testes US-05 (aprovado, duplicado, retorno-sem-webhook).
- **Saída:** pedido vira `paid` só por webhook válido; idempotente.

## M5 — Entrega segura
**Objetivo:** fechar o fluxo de valor.
- `DownloadGrant` na aprovação; `GET /download/<token>/` (RF-30,31,33 / RNF-03).
- Expiração e limite; arquivo protegido.
- Testes US-06.
- **Saída:** quem pagou baixa; expira/limita corretamente. **➡️ MVP completo.**

---

## Pós-MVP (M6+)

- E-mail transacional com link (RF-32).
- Marca d'água no PDF (anti-pirataria) — [`20`](20-entrega-ebook-anti-pirataria.md).
- Conta de leitor + histórico (RF-52).
- Busca/filtros avançados (RF-04), categorias ricas.
- Cupons (RF-26), relatórios (RF-42).
- Decisão e implementação do **frontend dedicado/separado** (ADR-005).
- CD automatizado + hospedagem de produção (custo baixo).

---

## Notas

- **Ordem é incremental e testável:** cada marco entrega algo demonstrável.
- Datas não fixadas aqui de propósito — definir conforme disponibilidade do Micael.
- Dependências: M4 depende de M3; M5 depende de M4.
