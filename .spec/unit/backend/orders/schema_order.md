# Unit: OrderCreateIn / OrderOut (`schema`)

> Tipo: `schema` (Pydantic) · Área: `backend/orders`
> Deriva de: [`planning/11`](../../../planning/11-contratos-api.md) §3 · RF-20 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Schemas de entrada/saída do pedido na API.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/orders/schemas.py` (`OrderCreateIn`, `OrderOut`) |
| Teste | `backend/tests/orders/test_schema_order.py` |

## 3. Contrato

```python
class OrderCreateIn(BaseModel):
    product_slug: str
    buyer_email: EmailStr


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference: UUID
    status: OrderStatus
    amount: Decimal
    checkout_url: str | None = None
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `model_order` | serialização |

## 5. Comportamento / regras

- `EmailStr` valida o e-mail automaticamente (erro `422` se inválido).
- `checkout_url` presente na criação; ausente ao consultar status.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Entrada válida | parseia ok |
| T2 | E-mail inválido | erro de validação |
| T3 | Serializar Order | retorna `reference`/`status`/`amount` |

## 7. Rastreabilidade

- RF-20,25 · Units: `router_orders`, `service_create_order`

## 8. Pendências

- [ ] Multi-item na entrada (lista de slugs) — visão completa.
