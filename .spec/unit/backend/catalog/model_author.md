# Unit: Author / ProductAuthor (`model`)

> Tipo: `model` · Área: `backend/catalog` · Tier 🟡
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Autoria estruturada: `author` e associação N:N `product_author` (substitui o campo
texto `product.author`).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/models.py` (`Author`, `ProductAuthor`) |
| Teste | `backend/tests/catalog/test_model_author.py` |

## 3. Contrato

```python
class Author(Base):
    __tablename__ = "author"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(180), unique=True)
    bio: Mapped[str] = mapped_column(Text, default="")


class ProductAuthor(Base):
    __tablename__ = "product_author"
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"), primary_key=True)
```

## 4. Comportamento / regras

- Um produto pode ter vários autores e vice-versa.
- Migração: campo texto `product.author` → `Author`/`ProductAuthor` (manter compat durante a transição).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Produto com 2 autores | ambos associados |
| T2 | Slug de autor duplicado | viola UNIQUE |

## 6. Rastreabilidade

- RF-01,02 · Units: `model_product`, `schema_product` (incluir autores)

## 7. Pendências

- [ ] Estratégia de migração do campo texto.
