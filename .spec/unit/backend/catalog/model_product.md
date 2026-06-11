# Unit: Product (`model`)

> Tipo: `model` · Área: `backend/catalog`
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md), [`planning/09`](../../../planning/09-modelo-de-dominio.md), [`10`](../../../planning/10-modelo-de-dados.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Mapear a tabela `product` (e-book à venda) e suas invariantes básicas.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/models.py::Product` |
| Teste | `backend/tests/catalog/test_model_product.py` |

## 3. Contrato

```python
class ProductStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(220), unique=True)
    author: Mapped[str] = mapped_column(String(160))          # texto no MVP; multi-autor depois
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    cover: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file: Mapped[str | None] = mapped_column(String(500), nullable=True)  # path protegido
    status: Mapped[ProductStatus] = mapped_column(default=ProductStatus.DRAFT)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("category.id"), nullable=True)
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/db_session` (Base) | mapeamento |
| `model_category` | FK |

## 5. Comportamento / regras

- `price >= 0` (CHECK em [`db/constraints`](../../db/README.md)).
- Apenas `status == PUBLISHED` aparece no catálogo (RF-01).
- Publicar exige `file` presente (validação no service/admin) — ver `service`/`router`.
- `file` aponta para volume protegido (RNF-03), nunca servido publicamente.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Criar produto rascunho | persiste com `status=draft` |
| T2 | Preço negativo | viola CHECK |
| T3 | Slug duplicado | viola UNIQUE |

## 7. Rastreabilidade

- RF-01,02,10,11 · [`db/schema_overview`](../../db/schema_overview.md)
- Units: `schema_product`, `service_list_products`, `db/constraints`

## 8. Pendências

- [ ] `author` texto agora vs migrar para `author`/`product_author` (visão completa).
