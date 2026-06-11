# Unit: ProductCatalog.get_by_slug (`service`)

> Tipo: `service` · Área: `backend/catalog`
> Deriva de: US-02 · RF-02 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Obter o detalhe de um produto **publicado** pelo `slug`.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/services.py::ProductCatalog.get_by_slug` |
| Teste | `backend/tests/catalog/test_get_product.py` |

## 3. Contrato

```python
class ProductCatalog:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_slug(self, slug: str) -> Product:
        ...  # levanta ProductNotFound se não existir ou não estiver publicado
```

- **Erros:** `ProductNotFound` (404 no router).

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `session` / `model_product` | consulta | real |

## 5. Comportamento / regras

- Só retorna `published`; rascunho → `ProductNotFound` (não vazar existência).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Slug publicado | retorna o produto |
| T2 | Slug de rascunho | `ProductNotFound` |
| T3 | Slug inexistente | `ProductNotFound` |

## 7. Rastreabilidade

- US-02 · RF-02 · Units: `model_product`, `schema_product`, `router_products`

## 8. Pendências

- [ ] Mensagem de erro genérica (não revelar rascunho).
