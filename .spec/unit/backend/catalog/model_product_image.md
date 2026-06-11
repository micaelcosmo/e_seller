# Unit: ProductImage (`model`)

> Tipo: `model` · Área: `backend/catalog` · Tier 🟡
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Imagens do produto (capa + extras), substituindo o `product.cover` único.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/models.py::ProductImage` |
| Teste | `backend/tests/catalog/test_model_product_image.py` |

## 3. Contrato

```python
class ProductImage(Base):
    __tablename__ = "product_image"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    url: Mapped[str] = mapped_column(String(500))   # media público
    is_cover: Mapped[bool] = mapped_column(default=False)
    position: Mapped[int] = mapped_column(default=0)
```

## 4. Comportamento / regras

- Exatamente uma `is_cover=True` por produto (regra no service/validação).
- Imagens são públicas (volume `media`), diferente do arquivo do e-book.

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Definir capa | uma `is_cover` por produto |
| T2 | Ordenação | respeita `position` |

## 6. Rastreabilidade

- Units: `model_product`, `schema_product` (`cover_url`)

## 7. Pendências

- [ ] Garantir unicidade da capa (constraint parcial vs validação).
