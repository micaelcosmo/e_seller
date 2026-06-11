# Unit: ProductOut / ProductListItem (`schema`)

> Tipo: `schema` (Pydantic) · Área: `backend/catalog`
> Deriva de: [`planning/11`](../../../planning/11-contratos-api.md) §2 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Schemas de saída do produto na API (lista e detalhe), **sem** expor o arquivo do e-book.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/schemas.py` (`ProductListItem`, `ProductOut`) |
| Teste | `backend/tests/catalog/test_schema_product.py` |

## 3. Contrato

```python
class ProductListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    title: str
    author: str
    price: Decimal
    cover_url: str | None = None


class ProductOut(ProductListItem):
    description: str
    category: str | None = None
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `model_product` | serialização |

## 5. Comportamento / regras

- **Nunca** inclui `file` (path do e-book) — RNF-03.
- `cover_url` derivado do `cover` (URL pública).
- `price` como `Decimal` (precisão monetária).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Serializar produto | inclui slug/title/price; **não** inclui `file` |
| T2 | Detalhe | inclui `description` e `category` |

## 7. Rastreabilidade

- RF-01,02 · RNF-03 · Units: `service_list_products`, `service_get_product`, `router_products`

## 8. Pendências

- [ ] Formato de `cover_url` (relativo vs absoluto por ambiente).
