# Gateway de Pagamento Fake (PAY-03)

> Trilha api · e_seller · 2026-06-10

O gateway fake é o provedor de pagamento padrão em ambiente `dev` e `test`.
Substitui o Mercado Pago real (PAY-01) sem exigir conta ou credenciais externas.

---

## Como funciona

1. `POST /api/v1/orders` cria o pedido com `status=PENDING`.
2. `CheckoutService.create_for(order)` chama `FakePaymentGateway.create_checkout()`.
3. O gateway retorna uma URL de simulação: `/pay/simulate/{order_reference}`.
4. O usuário acessa a URL e escolhe: **Aprovado**, **Recusado** ou **Pendente**.
5. O formulário faz `POST /pay/confirm/{reference}` com o status escolhido.
6. O backend simula um webhook: `POST /api/v1/payments/webhook` com payload fake.
7. O `WebhookProcessor` processa idempotente e atualiza o pedido.

---

## Ativação

Controlado por `Settings.payment_provider`:

| Valor | Gateway ativo |
|---|---|
| `fake` (padrão) | `FakePaymentGateway` |
| `mercadopago` | `MercadoPagoGateway` (PAY-01) |

```env
PAYMENT_PROVIDER=fake  # dev/test
PAYMENT_PROVIDER=mercadopago  # produção
```

---

## Fluxo de teste sem frontend

```bash
# 1. Criar pedido (guest ou autenticado)
curl -X POST http://localhost:48080/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"product_slug": "fastapi-do-zero", "buyer_email": "test@x.com"}'
# Retorna: {"reference": "ABC123", ...}

# 2. Simular aprovação via webhook direto
curl -X POST http://localhost:48080/api/v1/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{"provider_payment_id": "fake-ABC123", "order_reference": "ABC123", "provider_status": "approved"}'
# Retorna: {"outcome": "processed", ...}

# 3. Verificar estado do pedido
curl http://localhost:48080/api/v1/orders/ABC123
# status: "paid"
```

---

## Segurança (gateway fake)

- Em `payment_provider=mercadopago`, a assinatura `x-signature` é **obrigatória**
  (`WebhookSignatureValidator`). Sem segredo configurado, webhooks reais falham.
- Em `payment_provider=fake`, a assinatura não é validada (ambiente de dev/test).
- **Nunca use `PAYMENT_PROVIDER=fake` em produção.**

---

## Arquivos relevantes

| Arquivo | Responsabilidade |
|---|---|
| `app/payments/gateways.py` | `FakePaymentGateway` e protocolo `PaymentGateway` |
| `app/payments/router.py` | Recebe webhook; valida assinatura se MP |
| `app/web/router.py` | Página `/pay/simulate/` e `/pay/confirm/` |
| `app/payments/status_map.py` | Mapeamento provider_status → OrderStatus |
