# Unit: CategoryOut (`schema`)

> Tipo: `schema` (Pydantic) · Área: `backend/catalog`
> Deriva de: [`planning/11`](../../../planning/11-contratos-api.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Schema de saída de categoria na API.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/schemas.py::CategoryOut` |
| Teste | `backend/tests/catalog/test_schema_category.py` |

## 3. Contrato

```python
class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    slug: str
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `model_category` | serialização (`from_attributes`) |

## 5. Comportamento / regras

- Não expõe `id` interno (usa `slug`).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Serializar Category | retorna `name`/`slug` |

## 7. Rastreabilidade

- RF-13 · Units: `router_categories`

## 8. Pendências

- [ ] Incluir contagem de produtos por categoria?
