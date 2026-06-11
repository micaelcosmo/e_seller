# 10 — Modelo de Dados

> Documento de planning · e_seller · 2026-06-06
> Tradução do domínio ([`09`](09-modelo-de-dominio.md)) para o modelo relacional
> (PostgreSQL) e o mapeamento em models **SQLAlchemy** (migrations via **Alembic**).

---

## 1. Diagrama Entidade-Relacionamento (ER)

```
┌──────────────┐        ┌─────────────────────┐
│  category    │        │   product           │
│──────────────│        │─────────────────────│
│ id (PK)      │1      *│ id (PK)             │
│ name         │────────│ category_id (FK,nul)│
│ slug (uniq)  │        │ title               │
└──────────────┘        │ slug (uniq)         │
                        │ author              │
                        │ description         │
                        │ price (numeric)     │
                        │ cover (path)        │
                        │ file (path)         │
                        │ status              │
                        │ created_at          │
                        │ updated_at          │
                        └─────────┬───────────┘
                                  │1
                                  │
                                  │*
                        ┌─────────▼───────────┐        ┌────────────────────────┐
                        │   order             │1      1│   payment              │
                        │─────────────────────│────────│────────────────────────│
                        │ id (PK)             │        │ id (PK)                │
                        │ reference (uuid,uq) │        │ order_id (FK, uniq)    │
                        │ buyer_email         │        │ provider               │
                        │ product_id (FK)     │        │ provider_payment_id(uq)│
                        │ unit_price (numeric)│        │ status                 │
                        │ amount (numeric)    │        │ raw_payload (jsonb)    │
                        │ status              │        │ processed_at           │
                        │ created_at          │        │ created_at             │
                        │ updated_at          │        └────────────────────────┘
                        └─────────┬───────────┘
                                  │1
                                  │*
                        ┌─────────▼───────────┐
                        │  download_grant     │
                        │─────────────────────│
                        │ id (PK)             │
                        │ order_id (FK)       │
                        │ token (uniq)        │
                        │ expires_at          │
                        │ max_downloads (int) │
                        │ download_count (int)│
                        │ created_at          │
                        └─────────────────────┘
```

## 2. Tabelas e colunas

### `category`
| Coluna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| name | varchar(120) | |
| slug | varchar(140) | único |

### `product`
| Coluna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| category_id | bigint FK → category | nulo |
| title | varchar(200) | |
| slug | varchar(220) | único |
| author | varchar(160) | |
| description | text | |
| price | numeric(10,2) | ≥ 0 (CHECK) |
| cover | varchar(path) | imagem |
| file | varchar(path) | **arquivo protegido** (fora de media público) |
| status | varchar(16) | `draft`/`published` |
| created_at / updated_at | timestamptz | |

Índices: `slug`, `status` (catálogo filtra por `published`).

### `order`
| Coluna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| reference | uuid | único, usado em URLs |
| buyer_email | varchar(254) | |
| product_id | bigint FK → product | |
| unit_price | numeric(10,2) | congelado |
| amount | numeric(10,2) | total |
| status | varchar(16) | máquina de estados |
| created_at / updated_at | timestamptz | |

Índices: `reference`, `status`, `buyer_email`.

### `payment`
| Coluna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| order_id | bigint FK → order | **único** (1–1 no MVP) |
| provider | varchar(32) | `mercadopago` |
| provider_payment_id | varchar(64) | **único** → idempotência |
| status | varchar(24) | mapeado do provedor |
| raw_payload | jsonb | auditoria |
| processed_at | timestamptz | nulo até processar |
| created_at | timestamptz | |

### `download_grant`
| Coluna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| order_id | bigint FK → order | |
| token | varchar(64) | único, secreto |
| expires_at | timestamptz | |
| max_downloads | int | default p.ex. 5 |
| download_count | int | default 0 |
| created_at | timestamptz | |

## 3. Integridade e regras no banco

- `product.price >= 0` e `order.amount >= 0` via **CHECK**.
- `payment.provider_payment_id` **UNIQUE** garante idempotência mesmo sob corrida.
- `download_grant.token` **UNIQUE** e gerado com gerador seguro.
- FKs com `ON DELETE` pensados: não apagar `product` com pedidos pagos (proteger histórico).

> 💡 *No SQLAlchemy:* essas tabelas viram classes mapeadas (estilo 2.x, com
> `Mapped[...]` e `mapped_column(...)`) em `models.py` de cada módulo. Os tipos
> `numeric` → `Numeric`, `jsonb` → `JSONB`/`JSON`, `uuid` → `Uuid`,
> `timestamptz` → `DateTime(timezone=True)`. O **Alembic** gera e versiona as
> migrations a partir desses models.

## 4. Dados de exemplo (seed para testes/dev)

- 3 produtos publicados + 1 rascunho.
- 1 pedido em cada estado relevante (`pending`, `paid`, `failed`).
- Útil para os cenários de [`05-user-stories.md`](05-user-stories.md).

## 5. Pendências

- [ ] Definir `max_downloads` e janela de expiração padrão (sugestão: 5 downloads / 7 dias).
- [ ] Política de retenção de `raw_payload` (LGPD — ver [`19`](19-seguranca-e-lgpd.md)).
