# Unit: Tag / ProductTag (`model`)

> Tipo: `model` · Área: `backend/catalog` · Tier 🟡
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Marcação livre/facetas: `tag` e N:N `product_tag`.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/models.py` (`Tag`, `ProductTag`) |
| Teste | `backend/tests/catalog/test_model_tag.py` |

## 3. Contrato

```python
class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)


class ProductTag(Base):
    __tablename__ = "product_tag"
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id"), primary_key=True)
```

## 4. Comportamento / regras

- Tags reutilizáveis entre produtos; úteis para busca/filtro (RF-04).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Associar tags a produto | persistem |
| T2 | Tag duplicada | viola UNIQUE |

## 6. Rastreabilidade

- RF-04 · Units: `model_product`, `service_search_products`

## 7. Pendências

- [ ] Filtro por tag no endpoint de catálogo.
