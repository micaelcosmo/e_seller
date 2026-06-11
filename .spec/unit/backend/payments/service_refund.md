# Unit: RefundService (`service`)

> Tipo: `service` · Área: `backend/payments` · Tier 🟡
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Processar estorno: registrar `Refund`, transicionar o pedido e revogar a entrega.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/payments/services.py::RefundService` |
| Teste | `backend/tests/payments/test_refund_service.py` |

## 3. Contrato

```python
class RefundService:
    def __init__(self, session: Session, gateway: PaymentGateway) -> None:
        self.session = session
        self.gateway = gateway

    def process(self, payment: Payment, amount: Decimal) -> Refund:
        ...  # idempotente por provider_refund_id; RefundInvalid se amount > pago
```

## 4. Comportamento / regras

- Idempotente por `provider_refund_id` (igual à idempotência do webhook).
- Transiciona pedido `paid → refunded` (via `OrderStateMachine`).
- **Revoga entrega:** invalida `DownloadGrant` ativos e (decisão) o `entitlement`.
- `amount` não pode exceder o pago.

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Estorno total | pedido `refunded`; grants invalidados |
| T2 | Estorno repetido | idempotente |
| T3 | Valor > pago | `RefundInvalid` |

## 6. Rastreabilidade

- Units: `model_refund`, `orders/service_state_machine`, `delivery/service_validate_grant`, `entitlement/service_grant_entitlement`

## 7. Pendências

- [ ] Estorno revoga `entitlement` (posse) ou só bloqueia novo download?
