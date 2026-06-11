# Unit: router_products (`router`)

> Tipo: `router` · Área: `backend/catalog`
> Deriva de: [`planning/11`](../../../planning/11-contratos-api.md) §2 · RF-01,02,03 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Expor os endpoints públicos de catálogo, delegando ao `ProductCatalog`.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/router_products.py` |
| Teste | `backend/tests/catalog/test_router_products.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/products", tags=["catalog"])


@router.get("", response_model=list[ProductListItem])
def list_products(q: str | None = None, limit: int = 20, offset: int = 0,
                  catalog: ProductCatalog = Depends(get_product_catalog)): ...


@router.get("/{slug}", response_model=ProductOut)
def get_product(slug: str, catalog: ProductCatalog = Depends(get_product_catalog)): ...
```

- **Saída:** `200` com lista/detalhe; `404` se não encontrado.

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `service_list_products`/`get`/`search` | regra | real |
| `schema_product` | serialização | real |
| `tests/conftest_client` | client httpx | teste |

## 5. Comportamento / regras

- `q` presente → usa `search`; ausente → `list_published`.
- Router só faz HTTP; nenhuma regra de negócio aqui.
- Traduz `ProductNotFound` → `404`.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | GET /api/products | `200` lista de publicados |
| T2 | GET /api/products?q=termo | `200` resultados da busca |
| T3 | GET /api/products/{slug} publicado | `200` detalhe |
| T4 | GET /api/products/{slug} inexistente | `404` |

## 7. Rastreabilidade

- RF-01,02,03 · US-01,02 · Units: services de catalog, `schema_product`

## 8. Pendências

- [ ] Formato de paginação na resposta (envelope vs lista pura).
