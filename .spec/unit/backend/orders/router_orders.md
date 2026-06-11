# Unit: router_orders (`router`)

> Tipo: `router` · Área: `backend/orders`
> Deriva de: [`planning/11`](../../../planning/11-contratos-api.md) §3 · RF-20,25 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Expor criação de pedido e consulta de status.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/orders/router.py` |
| Teste | `backend/tests/orders/test_router_orders.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
def create_order(data: OrderCreateIn, creator: OrderCreator = Depends(get_order_creator)): ...


@router.get("/{reference}", response_model=OrderOut)
def get_order(reference: UUID, reader: OrderReader = Depends(get_order_reader)): ...
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `service_create_order` / `service_get_order` | regra |
| `schema_order` | I/O |

## 5. Comportamento / regras

- `POST` cria pedido e retorna `201` com `checkout_url`.
- `404` para `ProductNotFound`/`OrderNotFound`; `422` para entrada inválida.
- Sem regra de negócio no router.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | POST válido | `201` com `reference`/`checkout_url`/`pending` |
| T2 | POST e-mail inválido | `422` |
| T3 | POST produto inexistente | `404` |
| T4 | GET reference válida | `200` status do pedido |
| T5 | GET reference inexistente | `404` |

## 7. Rastreabilidade

- RF-20,25 · US-04 · Units: services de orders, `schema_order`

## 8. Pendências

- [ ] Endpoint de "retorno" do checkout (não libera download — RNF-01).
