# .spec/frontend/

Trilha **viva** de **frontend(s)** do e_seller — serviços separados do backend, que
consomem a API JSON (ver [`../api/`](../api/)).

## Frontends

| Frontend | Papel | Stack | Porta |
|---|---|---|---|
| **storefront** | Loja: catálogo, compra, "Minha Biblioteca" — voltado ao cliente | **Next.js (React, SSR)** | 48173 |
| **dashboard-ui** | UI do [dashboard de evolução](../dashboard/) do projeto (gráficos) | Mesma stack + lib de gráficos (Recharts/Chart.js) | 48088 |

> Decisão de stack em [`adr-stack.md`](adr-stack.md).
> `self_reflection` **não** é frontend — é a prática de auto-revisão do código
> (ver [`../self_reflection/`](../self_reflection/)).

## Documentos

| Doc | Assunto |
|---|---|
| [`adr-stack.md`](adr-stack.md) | Decisão de stack (Next.js) e renderização do dashboard. |
| [`storefront.md`](storefront.md) | Páginas, componentes, fluxo e integração com a API. |
| [`dashboard-ui.md`](dashboard-ui.md) | UI do dashboard de evolução (gráficos). |
| [`conventions.md`](conventions.md) | Convenções de código do frontend (TS, idioma, estrutura). |

## Princípios

- **Separado do backend**; consome a API (`/api/v1`) e o OpenAPI ([`../api/openapi-workflow.md`](../api/openapi-workflow.md)).
- **Custo zero**, open-source. Portas não-padrão ([`../unit/infra/ports.md`](../unit/infra/ports.md)).
- Idioma: **código em inglês; comentários em pt-BR** (mesma regra dos [`../standards/`](../standards/)).

## Regra de manutenção

Trilha viva: atualizar aqui e no [`CHANGELOG.md`](CHANGELOG.md) a cada evolução do frontend.
