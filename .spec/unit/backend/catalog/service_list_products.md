# Unit: ProductCatalog.list_published (`service`)

> Tipo: `service` · Área: `backend/catalog`
> Deriva de: US-01 · RF-01 · [`planning/11`](../../../planning/11-contratos-api.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Listar produtos **publicados**, paginados, para o catálogo.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/services.py::ProductCatalog.list_published` |
| Teste | `backend/tests/catalog/test_list_products.py` |

## 3. Contrato

```python
class ProductCatalog:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_published(self, *, limit: int = 20, offset: int = 0) -> list[Product]:
        ...
```

- **Saída:** lista de `Product` com `status == published`, ordenada (ex.: por `created_at` desc).
- **Erros:** nenhum (lista vazia se não houver).

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `session` | consulta | real (DB de teste) |
| `model_product` | entidade | real |

## 5. Comportamento / regras

- Filtra **apenas** `published` (rascunhos nunca aparecem) — RF-01.
- Paginação por `limit`/`offset`.
- Iteração/montagem com **laço explícito** quando necessário (sem comprehension — [`oop-and-naming`](../../../standards/oop-and-naming.md)).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | 3 publicados + 1 rascunho | retorna 3; rascunho ausente |
| T2 | Paginação | `limit=2, offset=2` retorna o 3º |
| T3 | Catálogo vazio | retorna `[]` |

## 7. Rastreabilidade

- US-01 · RF-01 · Units: `model_product`, `schema_product`, `router_products`

## 8. Pendências

- [ ] Ordenação padrão (mais recentes? destaque?).
