# Unit: Refund (`model`)

> Tipo: `model` · Área: `backend/payments` · Tier 🟡
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md), [`planning/18`](../../../planning/18-pagamentos-mercado-pago.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Registrar estornos (parciais/totais) de um pagamento.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/payments/models.py::Refund` |
| Teste | `backend/tests/payments/test_model_refund.py` |

## 3. Contrato

```python
class Refund(Base):
    __tablename__ = "refund"
    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payment.id"))
    provider_refund_id: Mapped[str] = mapped_column(String(64), unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(24))
    created_at: Mapped[datetime]
```

## 4. Comportamento / regras

- `provider_refund_id` único → idempotência do estorno (mesmo padrão do pagamento).
- `amount` ≤ valor do pagamento (CHECK/validação).
- Estorno aprovado leva o pedido a `refunded` (via `OrderStateMachine`).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Criar estorno | persiste |
| T2 | `provider_refund_id` duplicado | viola UNIQUE |

## 6. Rastreabilidade

- Units: `service_refund`, `model_payment`, `orders/service_state_machine`

## 7. Pendências

- [ ] Estorno via webhook do MP vs ação manual no admin.
