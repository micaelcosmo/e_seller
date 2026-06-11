# Unit: BillingService (`service`)

> Tipo: `service` · Área: `backend/billing` · Tier 🔵
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Gerenciar o perfil fiscal e (futuro) acionar emissão de NF a partir de um pedido pago.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/billing/services.py::BillingService` |
| Teste | `backend/tests/billing/test_billing_service.py` |

## 3. Contrato

```python
class BillingService:
    def __init__(self, session: Session, invoicer: Invoicer) -> None:  # Invoicer = Protocol (gateway NF)
        self.session = session
        self.invoicer = invoicer

    def upsert_profile(self, user: User | None, data: BillingData) -> BillingProfile: ...
    def issue_invoice(self, order: Order) -> InvoiceResult:
        ...  # só para pedido 'paid'; idempotente por pedido
```

## 4. Comportamento / regras

- `Invoicer` é abstração (Protocol) → testável com fake (DIP), igual ao gateway de pagamento.
- `issue_invoice` só para pedido `paid`; idempotente por pedido.
- Validação de CPF/CNPJ.

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Upsert perfil | cria/atualiza |
| T2 | Emitir NF de pedido pago | aciona invoicer (fake) |
| T3 | Emitir 2x | idempotente |
| T4 | Pedido não pago | recusa |

## 6. Rastreabilidade

- Units: `model_billing_profile`, `orders/model_order`, `payments/service_process_webhook`

## 7. Pendências

- [ ] Escolher provedor de NF e o contrato do `Invoicer`.
