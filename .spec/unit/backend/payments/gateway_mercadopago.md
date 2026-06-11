# Unit: PaymentGateway / MercadoPagoGateway (`gateway`)

> Tipo: `gateway` (integração externa) · Área: `backend/payments`
> Deriva de: [`planning/18`](../../../planning/18-pagamentos-mercado-pago.md) · ADR-001/004 ·
> Padrões: [`../../../standards/`](../../../standards/) (DIP, Protocol) · Status: **Rascunho**

---

## 1. Objetivo

Isolar a comunicação com o Mercado Pago atrás de uma **abstração (Protocol)**, para
que os services dependam da interface e os testes usem um fake.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/payments/gateways/mercadopago.py` (`PaymentGateway`, `MercadoPagoGateway`) |
| Teste | `backend/tests/payments/test_gateway_mercadopago.py` |

## 3. Contrato

```python
class PaymentGateway(Protocol):
    def create_checkout(self, order: Order) -> CheckoutData: ...
    def fetch_payment(self, provider_payment_id: str) -> PaymentData: ...


class MercadoPagoGateway:
    def __init__(self, access_token: str, environment: str, http: HttpClient) -> None:
        self.access_token = access_token
        self.environment = environment
        self.http = http
```

- **Erros:** `GatewayError`/`PaymentLookupError` em falhas de rede/HTTP.

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| cliente HTTP (`httpx`) | chamar a API | **mock** (`respx`) |
| `core/config` (token/env) | credenciais | injetado |

## 5. Comportamento / regras

- Implementa o Protocol `PaymentGateway` (LSP: o fake substitui sem quebrar).
- Não contém regra de negócio (só I/O + mapeamento de payload).
- `fetch_payment` consulta a fonte (não confiar no corpo do webhook).
- Credenciais via injeção; nunca hardcoded (RNF-04).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | create_checkout ok | retorna `CheckoutData` com `checkout_url` |
| T2 | fetch_payment ok | retorna `PaymentData` com status |
| T3 | erro HTTP transitório | `PaymentLookupError` |
| T4 | fake implementa Protocol | substituível nos testes |

## 7. Rastreabilidade

- RF-22,23 · ADR-001/004 · Units: `service_create_checkout`, `service_process_webhook`

## 8. Pendências

- [ ] Checkout Pro (redirect) vs transparente.
- [ ] Sync vs async (alinha com driver/serviços).
