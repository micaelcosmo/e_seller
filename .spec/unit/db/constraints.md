# Unit: constraints (`migration`/integridade)

> Tipo: `migration` (integridade) · Área: `db`
> Deriva de: [`db/schema_overview`](schema_overview.md), [`planning/10`](../../planning/10-modelo-de-dados.md) ·
> RNF-20 · Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Definir as constraints de integridade que protegem as regras de negócio no nível do banco.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | nas migrations / `__table_args__` dos models |
| Teste | `backend/tests/db/test_constraints.py` |

## 3. Constraints (MVP)

| Constraint | Tabela | Regra |
|---|---|---|
| UNIQUE | `payment.provider_payment_id` | idempotência do webhook (RNF-20) |
| UNIQUE | `download_grant.token` | token de download único |
| UNIQUE | `product.slug`, `category.slug` | slugs únicos |
| UNIQUE | `order.reference` | referência pública única |
| UNIQUE | `user.email` | conta única por e-mail |
| CHECK | `product.price >= 0` | preço não-negativo |
| CHECK | `order.amount >= 0` | valor não-negativo |
| CHECK | `download_grant.download_count >= 0` | contador não-negativo |
| FK | todas | `ON DELETE` que **proteja histórico** de vendas |

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `migration_initial` | onde são criadas |
| models do Tier 🟢 | colunas-alvo |

## 5. Comportamento / regras

- A UNIQUE de `provider_payment_id` é a salvaguarda final de idempotência sob corrida.
- `ON DELETE`: não permitir apagar `product` com `order_item` (RESTRICT) — proteger histórico.
- **Enum com `server_default`:** `Enum(<classe>)` do SQLAlchemy cria o tipo do Postgres com os
  **nomes** dos membros (`PENDING`, `APPROVED`...), não com os valores. O `server_default` de
  coluna enum usa, portanto, o **nome** do membro — senão o `create_all` num Postgres novo
  falha (`invalid input value for enum`) e o backend não sobe.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Inserir `provider_payment_id` duplicado | erro de UNIQUE |
| T2 | `product.price = -1` | erro de CHECK |
| T3 | Apagar produto com venda | bloqueado (RESTRICT) |
| T4 | `token` duplicado | erro de UNIQUE |
| T5 | Toda coluna enum com `server_default` (DDL compilado para Postgres) | o default é um dos rótulos do tipo enum |

## 7. Rastreabilidade

- RNF-20 · Planning [`10`](../../planning/10-modelo-de-dados.md) · Units: `model_payment`, `model_product`, `model_order`

## 8. Pendências

- [ ] Posse única e-book: UNIQUE (`user_id`, `product_id`) em `entitlement` (Tier 🟡).
