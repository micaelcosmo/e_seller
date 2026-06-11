# Unit: migration_initial (`migration`)

> Tipo: `migration` · Área: `db`
> Deriva de: [`db/schema_overview`](schema_overview.md), [`planning/10`](../../planning/10-modelo-de-dados.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Primeira migration: cria as tabelas do **Tier 🟢 (MVP)** com suas constraints/índices.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/alembic/versions/0001_initial.py` |
| Teste | `backend/tests/db/test_migration_initial.py` |

## 3. Conteúdo (escopo MVP)

Cria: `user`, `category`, `product`, `order`, `order_item`, `payment`, `download_grant`.
Inclui constraints e índices definidos em [`constraints`](constraints.md) e [`indexes`](indexes.md).

> Tiers 🟡/🔵 (author, coupon, review, wishlist, role, billing_profile, etc.) entram em
> **migrations posteriores**, conforme implementação (ver [`schema_overview`](schema_overview.md)).

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `alembic_setup` | infraestrutura |
| todos os `model_*` do Tier 🟢 | origem do schema |

## 5. Comportamento / regras

- `upgrade()` cria tabelas na ordem de dependência (FKs).
- `downgrade()` remove na ordem inversa.
- Determinística e revisável.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | upgrade em DB vazio | todas as 7 tabelas criadas |
| T2 | constraints presentes | UNIQUE/CHECK aplicadas (ver `constraints`) |
| T3 | downgrade | remove tudo sem erro |

## 7. Rastreabilidade

- Planning [`10`](../../planning/10-modelo-de-dados.md) · Units: `constraints`, `indexes`, `seeds`

## 8. Pendências

- [ ] Confirmar tipos exatos (Uuid nativo do Postgres, JSONB).
