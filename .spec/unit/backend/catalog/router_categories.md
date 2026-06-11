# Unit: router_categories (`router`)

> Tipo: `router` · Área: `backend/catalog`
> Deriva de: [`planning/11`](../../../planning/11-contratos-api.md) · RF-13 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Expor `GET /api/categories` (lista de categorias).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/router_categories.py` |
| Teste | `backend/tests/catalog/test_router_categories.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/categories", tags=["catalog"])


@router.get("", response_model=list[CategoryOut])
def list_categories(catalog: ProductCatalog = Depends(get_product_catalog)): ...
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `model_category` / service | consulta |
| `schema_category` | serialização |

## 5. Comportamento / regras

- Retorna categorias (hierarquia pode ser representada por `parent` no futuro).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | GET /api/categories | `200` com lista |
| T2 | Sem categorias | `200` `[]` |

## 7. Rastreabilidade

- RF-13 · Units: `model_category`, `schema_category`

## 8. Pendências

- [ ] Expor árvore (aninhada) vs lista plana.
