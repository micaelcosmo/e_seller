# 18 — Pagamentos (Mercado Pago)

> Documento de planning · e_seller · 2026-06-06
> Integração de pagamento e a regra crítica: **só entregar quando realmente pago**.

---

## 1. Por que Mercado Pago

- Cobre os meios de pagamento brasileiros: **Pix, cartão e boleto**.
- **Sandbox gratuito** para desenvolvimento (RNF-42).
- API + **webhooks** maduros.

## 2. Conceitos do Mercado Pago (resumo didático)

> 💡 *Como funciona, em alto nível:*
> 1. Criamos uma **preferência/checkout** (o que está sendo vendido e por quanto).
> 2. O cliente paga na interface do Mercado Pago (redirect ou checkout transparente).
> 3. O Mercado Pago nos avisa por **webhook** quando o status muda.
> 4. **Nós confirmamos** consultando a API (não confiamos só na notificação).

## 3. Fluxo de integração

```
orders.services.create_order(pendente)
   └─► payments.services.create_checkout(order)
          └─► [Mercado Pago] cria preference → checkout_url
   cliente paga
   └─► [Mercado Pago] POST /api/webhooks/mercadopago  (notificação)
          └─► validar assinatura (RNF-02)
          └─► consultar pagamento na API pelo id
          └─► mapear status → estado do pedido
          └─► idempotência por provider_payment_id (RNF-20)
          └─► se aprovado: order → paid + emitir DownloadGrant
```

## 4. Mapeamento de status

| Status Mercado Pago | Estado do Pedido (e_seller) |
|---|---|
| `approved` | `paid` |
| `pending` / `in_process` | `pending` |
| `rejected` | `failed` |
| `cancelled` | `cancelled` |
| `refunded` / `charged_back` | `refunded` |

## 5. Idempotência (requisito central)

- O Mercado Pago **pode reenviar** a mesma notificação várias vezes.
- Guardamos `provider_payment_id` **único** em `payment`.
- Processamento:
  1. Se já existe `payment` processado com aquele id → responder `200` e **não** repetir efeitos.
  2. Caso contrário → processar e registrar.
- Resultado: reentrega nunca cria pedido duplicado, grant duplicado ou e-mail duplicado.

```gherkin
Dado um pagamento já processado (provider_payment_id X)
Quando o webhook X chega de novo
Então respondemos 200 e nada muda
```

## 6. Segurança

- **Validar autenticidade** do webhook (assinatura/segredo) — RNF-02.
- **Nunca** liberar download pelo retorno do navegador — só pelo webhook confirmado (RNF-01).
- `MP_ACCESS_TOKEN` e `MP_WEBHOOK_SECRET` só via variáveis de ambiente (RNF-04).
- Guardar `raw_payload` para auditoria, respeitando retenção/LGPD ([`19`](19-seguranca-e-lgpd.md)).

## 7. Ambientes

| Ambiente | Mercado Pago |
|---|---|
| dev | **sandbox** (credenciais de teste) |
| test (CI) | **mockado** (sem rede) |
| prod | credenciais reais |

## 8. Tratamento de erros

- Falha ao criar checkout → pedido fica `pending`, cliente vê erro amigável e pode tentar de novo (RF-25).
- Erro transitório no webhook → responder com status que faça o Mercado Pago **reenviar**.
- Pagamento `rejected` → pedido `failed`, com opção de novo pagamento.

## 9. Testes (resumo)

- Criar checkout (gateway mockado) gera `checkout_url` e pedido `pending`.
- Webhook aprovado → `paid` + grant.
- Webhook duplicado → idempotente.
- Webhook sem assinatura válida → rejeitado.
- Retorno do navegador sem webhook → sem download.

## 10. Pendências

- [ ] Checkout **Pro (redirect)** vs **transparente** (definir; redirect é mais simples no MVP).
- [ ] Confirmar formato atual do payload e método de validação de assinatura na doc oficial.
- [ ] Política de reembolso/estorno (operacional).
