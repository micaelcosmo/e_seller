# Fluxograma — Backend (requisição e camadas)

> Trilha flowcharts · e_seller · 2026-06-07

## Camadas de uma requisição

```mermaid
flowchart LR
    C[Cliente / Frontend] -->|HTTP JSON| R[Router FastAPI]
    R -->|valida com| S[Schemas Pydantic]
    R -->|delega a| SV[Service - classe com DI]
    SV -->|persiste via| M[Models SQLAlchemy async]
    SV -->|integra com| G[Gateways - Mercado Pago]
    M --> DB[(PostgreSQL / asyncpg)]
    R -->|admin| ADM[SQLAdmin]
    SV -->|seguranca| SEC[JWT / token download / storage protegido]
```

## Fluxo crítico — compra → pagamento → entrega

```mermaid
flowchart TD
    A[POST /orders] --> B[OrderCreator: cria pedido pending, congela preco]
    B --> C[CheckoutService -> gateway -> checkout_url]
    C --> D[Cliente paga no provedor]
    D --> E[Webhook POST /webhooks/mercadopago]
    E --> F{provider_payment_id ja processado?}
    F -- Sim --> G[ALREADY_PROCESSED - idempotente]
    F -- Nao --> H[StatusMapper + maquina de estados]
    H -->|approved| I[Pedido = paid + emite DownloadGrant + Entitlement]
    H -->|rejected| J[Pedido = failed]
    I --> K[GET /download/token: valida expiracao/limite -> stream]
```

> Detalhes: [`../unit/backend/`](../unit/backend/) e [`../planning/08-arquitetura.md`](../planning/08-arquitetura.md).
