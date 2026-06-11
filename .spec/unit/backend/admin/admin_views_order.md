# Unit: OrderAdmin / PaymentAdmin (`admin`)

> Tipo: `admin` view · Área: `backend/admin`
> Deriva de: RF-40,41 · ADR-008 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Visualizar pedidos e pagamentos no painel (P2), em modo majoritariamente leitura.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/admin/views.py` (`OrderAdmin`, `PaymentAdmin`) |
| Teste | `backend/tests/admin/test_admin_order.py` |

## 3. Contrato

```python
class OrderAdmin(ModelView, model=Order):
    column_list = [Order.reference, Order.buyer_email, Order.status, Order.amount, Order.created_at]
    can_create = False
    can_delete = False


class PaymentAdmin(ModelView, model=Payment):
    column_list = [Payment.provider_payment_id, Payment.status, Payment.processed_at]
    can_create = False
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `orders/model_order`, `payments/model_payment` | dados |

## 5. Comportamento / regras

- Pedidos/pagamentos **não** são criados manualmente (fluxo é via API/webhook).
- Status alterável apenas de forma controlada (idealmente via ação, respeitando a máquina de estados).
- Sem expor dados pessoais além do necessário (LGPD).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Listar pedidos | mostra status/valor/data |
| T2 | Criar pedido pelo admin | desabilitado |

## 7. Rastreabilidade

- RF-40,41 · US-07 · Units: `orders/model_order`, `payments/model_payment`

## 8. Pendências

- [ ] Ações de estorno/cancelamento respeitando `OrderStateMachine`.
