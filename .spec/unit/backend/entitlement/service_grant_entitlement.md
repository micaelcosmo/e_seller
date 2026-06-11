# Unit: EntitlementService (`service`)

> Tipo: `service` · Área: `backend/entitlement` · Tier 🟡
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Conceder posse ao pagar e listar a biblioteca do usuário.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/entitlement/services.py::EntitlementService` |
| Teste | `backend/tests/entitlement/test_entitlement_service.py` |

## 3. Contrato

```python
class EntitlementService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def grant(self, order_item: OrderItem) -> Entitlement:
        ...  # idempotente: se já existe (user, product), retorna o existente
    def library(self, user: User) -> list[Product]: ...
    def owns(self, user: User, product_id: int) -> bool: ...
```

## 4. Comportamento / regras

- `grant` chamado quando o item é pago (junto da emissão do download — ver
  [`delivery/service_issue_download`](../delivery/service_issue_download.md)).
- **Idempotente** (respeita UNIQUE user/product).
- `owns` usado por reviews (comprador verificado) e cart (não recomprar).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Conceder ao pagar | posse criada |
| T2 | Conceder de novo | idempotente |
| T3 | library | lista os possuídos |
| T4 | owns | True/False correto |

## 6. Rastreabilidade

- Units: `model_entitlement`, `payments/service_process_webhook`, `delivery/service_issue_download`
