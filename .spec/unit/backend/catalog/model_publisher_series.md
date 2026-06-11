# Unit: Publisher / Series (`model`)

> Tipo: `model` · Área: `backend/catalog` · Tier 🔵
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Editora (`publisher`) e coleção/série (`series`) — agrupadores opcionais de produtos.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/models.py` (`Publisher`, `Series`) |
| Teste | `backend/tests/catalog/test_model_publisher_series.py` |

## 3. Contrato

```python
class Publisher(Base):
    __tablename__ = "publisher"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(180), unique=True)


class Series(Base):
    __tablename__ = "series"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(220), unique=True)
# Product ganha publisher_id e series_id (nuláveis) — ver model_product.
```

## 4. Comportamento / regras

- `product.publisher_id`/`series_id` nuláveis (opcionais).
- Apagar publisher/series não apaga produtos (FK nulável / RESTRICT).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Produto sem editora/série | válido (nulos) |
| T2 | Produtos da mesma série | agrupáveis |

## 6. Rastreabilidade

- Units: `model_product` (FKs), `schema_product`

## 7. Pendências

- [ ] Ordenação dentro da série (número do volume).
