# Unit: OrderReader.get_by_reference (`service`)

> Tipo: `service` · Área: `backend/orders`
> Deriva de: RF-25 · US-04 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Obter um pedido pela `reference` (UUID público) para acompanhamento de status.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/orders/services.py::OrderReader.get_by_reference` |
| Teste | `backend/tests/orders/test_get_order.py` |

## 3. Contrato

```python
class OrderReader:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_reference(self, reference: UUID) -> Order:
        ...  # levanta OrderNotFound
```

- **Erros:** `OrderNotFound` (404).

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `session` / `model_order` | consulta | real |

## 5. Comportamento / regras

- Busca por `reference`, nunca por `id`.
- Não expõe dados sensíveis além do necessário (status/amount).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Reference válida | retorna o pedido |
| T2 | Reference inexistente | `OrderNotFound` |

## 7. Rastreabilidade

- RF-25 · Units: `model_order`, `router_orders`

## 8. Pendências

- [ ] Restringir consulta ao próprio comprador (token/e-mail)?
