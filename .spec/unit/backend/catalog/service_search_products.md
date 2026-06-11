# Unit: ProductCatalog.search (`service`)

> Tipo: `service` · Área: `backend/catalog`
> Deriva de: US-01 · RF-03 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Buscar produtos publicados por título/autor.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/services.py::ProductCatalog.search` |
| Teste | `backend/tests/catalog/test_search_products.py` |

## 3. Contrato

```python
class ProductCatalog:
    def __init__(self, session: Session) -> None:
        self.session = session

    def search(self, query: str, *, limit: int = 20, offset: int = 0) -> list[Product]:
        ...
```

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `session` / `model_product` | consulta | real |

## 5. Comportamento / regras

- Busca case-insensitive em `title` e `author`, só `published`.
- `query` vazia → comportamento definido (retornar lista vazia ou todos? **decidir**).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Termo casa título | retorna correspondências publicadas |
| T2 | Termo casa autor | retorna correspondências |
| T3 | Sem correspondência | `[]` |
| T4 | Rascunho que casaria | não retorna |

## 7. Rastreabilidade

- RF-03 · Units: `model_product`, `router_products`

## 8. Pendências

- [ ] Busca simples (ILIKE) vs full-text (PostgreSQL `tsvector`) — começar simples.
