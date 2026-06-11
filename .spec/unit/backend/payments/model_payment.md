# Unit: Payment (`model`)

> Tipo: `model` · Área: `backend/payments`
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md), [`planning/18`](../../../planning/18-pagamentos-mercado-pago.md) ·
> RNF-20 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Mapear `payment` (registro de pagamento espelhando o Mercado Pago). Base da idempotência.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/payments/models.py::Payment` |
| Teste | `backend/tests/payments/test_model_payment.py` |

## 3. Contrato

```python
class Payment(Base):
    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    provider: Mapped[str] = mapped_column(String(32), default="mercadopago")
    provider_payment_id: Mapped[str] = mapped_column(String(64), unique=True)
    status: Mapped[str] = mapped_column(String(24))
    raw_payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    processed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime]
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/db_session` (Base) | mapeamento |
| `model_order` | FK |

## 5. Comportamento / regras

- `provider_payment_id` **UNIQUE** → salvaguarda de idempotência (RNF-20).
- `raw_payload` para auditoria (LGPD: retenção — [`security/lgpd`](../../security/README.md)).
- 1—* com `order` (várias tentativas); 1—* com `refund`.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Criar pagamento | persiste |
| T2 | `provider_payment_id` duplicado | viola UNIQUE |

## 7. Rastreabilidade

- RF-23,24 · RNF-20 · Units: `service_process_webhook`, `db/constraints`

## 8. Pendências

- [ ] Política de retenção de `raw_payload`.
