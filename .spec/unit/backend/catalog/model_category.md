# Unit: Category (`model`)

> Tipo: `model` · Área: `backend/catalog`
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md), [`planning/10`](../../../planning/10-modelo-de-dados.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Mapear a tabela `category` (classificação hierárquica de produtos).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/models.py::Category` |
| Teste | `backend/tests/catalog/test_model_category.py` |

## 3. Contrato

```python
class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(140), unique=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("category.id"), nullable=True)
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/db_session` (Base) | mapeamento |

## 5. Comportamento / regras

- `slug` único.
- `parent_id` permite hierarquia (auto-relação); raiz tem `parent_id = NULL`.
- Não impedir exclusão deixa produtos órfãos → ver `ON DELETE` em [`db/constraints`](../../db/README.md).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Criar categoria raiz | persiste com `parent_id` nulo |
| T2 | Subcategoria | `parent_id` aponta para a raiz |
| T3 | Slug duplicado | viola UNIQUE |

## 7. Rastreabilidade

- RF-13 · [`db/schema_overview`](../../db/schema_overview.md) · Units: `model_product`

## 8. Pendências

- [ ] Profundidade máxima da hierarquia (limitar?).
