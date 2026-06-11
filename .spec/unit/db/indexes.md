# Unit: indexes (`migration`/desempenho)

> Tipo: `migration` (índices) · Área: `db`
> Deriva de: [`db/schema_overview`](schema_overview.md), [`planning/10`](../../planning/10-modelo-de-dados.md) ·
> RNF-10 · Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Índices para as consultas mais frequentes (catálogo, busca, lookup de pedido/token).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | migrations / `__table_args__` |
| Teste | `backend/tests/db/test_indexes.py` |

## 3. Índices (MVP)

| Índice | Coluna(s) | Para quê |
|---|---|---|
| `ix_product_status` | `product.status` | filtrar catálogo (`published`) |
| `ix_product_slug` | `product.slug` (UNIQUE já cria) | detalhe por slug |
| `ix_product_title_author` | `product.title`, `product.author` | busca (RF-03) |
| `ix_order_reference` | `order.reference` (UNIQUE já cria) | lookup de pedido |
| `ix_order_status` | `order.status` | relatórios/admin |
| `ix_payment_provider_id` | `payment.provider_payment_id` (UNIQUE já cria) | webhook |
| `ix_grant_token` | `download_grant.token` (UNIQUE já cria) | download |

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `migration_initial` | onde são criados |

## 5. Comportamento / regras

- UNIQUE já gera índice (não duplicar).
- Busca: começar com índice B-tree; avaliar full-text (`tsvector`/GIN) depois.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Índices existem | presentes após migration |
| T2 | (opcional) plano de consulta usa índice | EXPLAIN usa o índice de status |

## 7. Rastreabilidade

- RNF-10 · RF-03 · Units: `migration_initial`, `catalog/service_search_products`

## 8. Pendências

- [ ] Full-text search (GIN) quando a busca crescer.
