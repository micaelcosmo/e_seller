# Unit: mercadopago_mock (`tests`/fixture)

> Tipo: `fixture` · Área: `tests`
> Deriva de: [`planning/13`](../../planning/13-estrategia-de-testes.md), [`18`](../../planning/18-pagamentos-mercado-pago.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Fornecer um **fake** do `PaymentGateway` (e/ou mock HTTP via `respx`) para testes sem rede.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/tests/fakes/mercadopago.py` (`FakePaymentGateway`) + fixture |

## 3. Contrato

```python
class FakePaymentGateway:  # implementa PaymentGateway (Protocol)
    def __init__(self, *, payment_status: str = "approved") -> None:
        self.payment_status = payment_status

    def create_checkout(self, order) -> CheckoutData: ...
    def fetch_payment(self, provider_payment_id) -> PaymentData: ...
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `payments/gateway_mercadopago` (Protocol) | contrato a implementar |
| `respx` (opcional) | mock HTTP |

## 5. Comportamento / regras

- Implementa o Protocol (LSP) → substitui o real sem quebrar.
- Configurável por cenário (`approved`/`rejected`/`pending`/erro).
- Nenhuma chamada de rede real.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | fake `approved` | `fetch_payment` retorna approved |
| T2 | fake erro | levanta `PaymentLookupError` |

## 7. Rastreabilidade

- Planning [`13`](../../planning/13-estrategia-de-testes.md) · Units: `payments/service_process_webhook`, `payments/service_create_checkout`

## 8. Pendências

- [ ] Fake do Protocol vs mock HTTP (respx) — usar fake por padrão.
