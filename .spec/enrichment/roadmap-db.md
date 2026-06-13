# Planning DB Enrichment

> Melhorias no PostgreSQL para o e_seller. Foco: full-text search, índices compostos
> e configuração de pool. Sem mudar schema de forma quebrada. Última atualização: 2026-06-13.

---

## 1. Full-Text Search (FTS) em Produtos

**Problema:** busca atual usa `ILIKE '%termo%'` — sem ranking, sem stemming, sem acentos,
sem suporte a frase. Lenta em tabelas grandes (seq scan).

**Solução:** coluna `search_vector: tsvector` em `products`, alimentada por trigger
(ou na inserção/atualização). Índice GIN. Busca via `to_tsquery` com `websearch_to_tsquery`.

**Schema:**
```sql
ALTER TABLE products ADD COLUMN search_vector tsvector;
CREATE INDEX ix_products_search_vector ON products USING GIN(search_vector);
```

**Trigger (Alembic DDL):**
```sql
CREATE OR REPLACE FUNCTION products_search_vector_update() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('portuguese', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('portuguese', coalesce(NEW.description, '')), 'B') ||
    setweight(to_tsvector('portuguese', coalesce(NEW.subtitle, '')), 'C');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER products_search_vector_trigger
  BEFORE INSERT OR UPDATE ON products
  FOR EACH ROW EXECUTE FUNCTION products_search_vector_update();
```

**SearchService:** `ProductSearchService(session)` com método `search(query, skip, limit)`:
```python
stmt = (
    select(Product)
    .where(Product.search_vector.op("@@")(func.websearch_to_tsquery("portuguese", query)))
    .order_by(func.ts_rank(Product.search_vector, func.websearch_to_tsquery("portuguese", query)).desc())
    .offset(skip)
    .limit(limit)
)
```

**Fallback:** se `search_vector IS NULL` (dados antigos sem trigger), recalcular via
`UPDATE products SET search_vector = ...` no migration.

**Endpoint:** `GET /api/v1/products?q=termo` continua igual; internamente usa FTS quando
`q` não é vazio. Compatível com frontend existente.

---

## 2. Índices Compostos

**Problema:** queries de relatório admin fazem scan em colunas combinadas sem índice composto.

| Query | Índice atual | Índice proposto |
|---|---|---|
| `WHERE status=X AND created_at>=Y` (orders) | ix_status | `(status, created_at)` |
| `WHERE product_id=X AND created_at>=Y` (reviews) | FK | `(product_id, created_at)` |
| `WHERE user_id=X AND created_at>=Y` (activity_log) | FK | `(user_id, created_at)` |
| `WHERE expires_at < now()` (revoked_tokens) | — | `(expires_at)` |

**Alembic DDL:**
```python
op.create_index("ix_orders_status_created", "orders", ["status", "created_at"])
op.create_index("ix_reviews_product_created", "reviews", ["product_id", "created_at"])
op.create_index("ix_activity_user_created", "user_activity_logs", ["user_id", "created_at"])
```

---

## 3. Connection Pool Tuning

**Problema:** pool padrão do SQLAlchemy async (pool_size=5, max_overflow=10) pode
causar timeouts em picos de tráfego.

**Configuração via Settings:**
```
db_pool_size: int = 10
db_pool_max_overflow: int = 20
db_pool_timeout: int = 30
db_pool_pre_ping: bool = True
```

**Aplicação em `core/db.py`:**
```python
engine = create_async_engine(
    url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_pool_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_pre_ping=settings.db_pool_pre_ping,
)
```

**Benefício:** elimina `TimeoutError` em picos; `pool_pre_ping` descarta conexões stale.

---

## 4. UML e Migração

Após adicionar `RevokedToken`, `ApiKey`, `UserActivityLog` e a coluna `search_vector`:

- Atualizar [`.spec/unit/db/uml-class-diagram.md`](../unit/db/uml-class-diagram.md).
- Gerar migration Alembic (`alembic revision --autogenerate -m "enrichment_aaa_fts"`).
- Testar migration up + down.

---

## 5. Seed Rico (para testar FTS)

Seeds atuais têm poucos produtos. Para testar FTS com ranking, precisamos de:
- 10+ produtos com títulos/descrições variados em pt-BR
- Acentos, sinônimos, termos compostos
- Arquivo: `backend/app/core/seeds_enrichment.json` (importado pelo seeder)

---

## Definition of Done

- [ ] `search_vector` coluna + índice GIN
- [ ] Trigger atualiza `search_vector` em INSERT/UPDATE
- [ ] `ProductSearchService` usa `websearch_to_tsquery`
- [ ] Endpoint `/products?q=` usa FTS (com fallback ILIKE em tests/SQLite)
- [ ] Índices compostos criados
- [ ] Pool tuning configurável via Settings
- [ ] Migration Alembic gerada e testada (up+down)
- [ ] UML atualizado
- [ ] Testes FTS (3+): busca com acentos, busca parcial, ranking
- [ ] Seed rico gerado
