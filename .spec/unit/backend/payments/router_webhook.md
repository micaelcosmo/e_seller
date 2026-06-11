# Unit: router_webhook (`router`)

> Tipo: `router` · Área: `backend/payments`
> Deriva de: [`planning/11`](../../../planning/11-contratos-api.md) §4 · RF-23,24 · RNF-02,11,20 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Receber o webhook do Mercado Pago, **validar a assinatura** e delegar ao `WebhookProcessor`.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/payments/router_webhook.py` |
| Teste | `backend/tests/payments/test_router_webhook.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/webhooks", tags=["payments"])


@router.post("/mercadopago", status_code=200)
def mercadopago_webhook(
    request: Request,
    notification: WebhookNotification = Depends(verify_webhook_signature),  # security/
    processor: WebhookProcessor = Depends(get_webhook_processor),
):
    result = processor.process(notification)
    return {"outcome": result.outcome}
```

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `security/webhook_signature` | validar autenticidade (RNF-02) | real |
| `service_process_webhook` (`WebhookProcessor`) | regra | real (gateway fake) |

## 5. Comportamento / regras

- Assinatura inválida → `401/403` (dependency rejeita) — RNF-02.
- Responde `200` rápido (RNF-11); idempotente (RNF-20) via o processor.
- Erro transitório → status que faça o MP **reenviar**.
- Sem regra de negócio no router.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Webhook válido aprovado | `200`; pedido vira `paid` |
| T2 | Assinatura inválida | `401/403`; sem efeito |
| T3 | Webhook duplicado | `200`; nada duplicado |
| T4 | Erro transitório do gateway | status de reenvio |

## 7. Rastreabilidade

- RF-23,24 · RNF-02,11,20 · US-05 · Units: `service_process_webhook`, `security/webhook_signature`

## 8. Pendências

- [ ] Formato exato do payload/headers de assinatura do MP.
