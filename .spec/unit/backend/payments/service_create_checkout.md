# Unit: CheckoutService (`service`)

> Tipo: `service` · Área: `backend/payments`
> Deriva de: US-04 · RF-22 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Gerar o checkout (preferência) no Mercado Pago para um pedido e retornar a `checkout_url`.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/payments/services.py::CheckoutService` |
| Teste | `backend/tests/payments/test_create_checkout.py` |

## 3. Contrato

```python
class CheckoutService:
    def __init__(self, gateway: PaymentGateway) -> None:
        self.gateway = gateway

    def create_for(self, order: Order) -> CheckoutData:
        ...  # delega ao gateway; levanta GatewayError em falha
```

- **Saída:** `CheckoutData` (contém `checkout_url`).
- **Erros:** `GatewayError`.

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `PaymentGateway` | criar preferência | **fake** |

## 5. Comportamento / regras

- Monta os dados do checkout a partir do pedido (itens, valor, `reference`).
- Não persiste nada (isso é do `OrderCreator`); apenas orquestra o gateway.
- Sem comprehension ao montar itens — laço explícito.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Pedido válido | retorna `CheckoutData` com `checkout_url` |
| T2 | Gateway falha | `GatewayError` propagado |

## 7. Rastreabilidade

- RF-22 · US-04 · Units: `gateway_mercadopago`, `orders/service_create_order`

## 8. Pendências

- [ ] Dados mínimos exigidos pela preferência (confirmar na doc do MP).
