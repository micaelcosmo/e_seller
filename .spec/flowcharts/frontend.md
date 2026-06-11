# Fluxograma — Frontend (Next.js)

> Trilha flowcharts · e_seller · 2026-06-07

## Arquitetura / dados

```mermaid
flowchart LR
    U[Usuario] --> P[Paginas Next.js - SSR/CSR]
    P --> H[Hooks / features por dominio]
    H --> API[Client gerado do OpenAPI]
    API -->|HTTP JSON| BE[Backend FastAPI /api/v1]
    P --> UI[Componentes reutilizaveis]
    subgraph Frontends
      P
      DASH[dashboard-ui - graficos da evolucao]
    end
    DASH --> DJSON[dashboard.json / GET /dashboard/data]
```

## Fluxo de uma ação (ex.: comprar)

```mermaid
flowchart TD
    A[Pagina do e-book] --> B{Usuario logado?}
    B -- Nao --> C[Login OU compra como convidado por e-mail]
    B -- Sim --> D[Usa dados da conta]
    C --> E[POST /orders]
    D --> E
    E --> F[Recebe checkout_url] --> G[Redireciona ao pagamento]
    G --> H[Polling GET /orders/reference]
    H -->|paid| I[Mostra download / Minha Biblioteca]
```

> Convenções: [`../frontend/conventions.md`](../frontend/conventions.md).
