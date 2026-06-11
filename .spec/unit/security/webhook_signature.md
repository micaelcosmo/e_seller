# Unit: verify_webhook_signature (`dependency`/security)

> Tipo: `dependency` · Área: `security`
> Deriva de: RNF-02 · RF-23 · [`planning/18`](../../planning/18-pagamentos-mercado-pago.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Validar a **autenticidade** do webhook do Mercado Pago antes de processá-lo.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/security/webhook.py::verify_webhook_signature` |
| Teste | `backend/tests/security/test_webhook_signature.py` |

## 3. Contrato

```python
def verify_webhook_signature(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> WebhookNotification:
    ...  # levanta InvalidSignature (401/403) se inválida; retorna a notificação parseada
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/config.mp_webhook_secret` | segredo de validação |
| headers/payload do request | base da assinatura |

## 5. Comportamento / regras

- Recalcula/compara a assinatura (HMAC) usando o segredo (comparação constante no tempo).
- Sem assinatura válida → rejeita (não processa) — RNF-02.
- Retorna `WebhookNotification` (ao menos `provider_payment_id`) para o router.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Assinatura válida | retorna notificação |
| T2 | Assinatura inválida | `InvalidSignature` |
| T3 | Header ausente | `InvalidSignature` |

## 7. Rastreabilidade

- RNF-02 · RF-23 · US-05 · Units: `payments/router_webhook`, `payments/service_process_webhook`

## 8. Pendências

- [ ] Formato exato do header/algoritmo de assinatura do MP (confirmar na doc).
