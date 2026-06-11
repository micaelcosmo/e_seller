# Unit: NewsletterService (`service`)

> Tipo: `service` · Área: `backend/newsletter` · Tier 🔵
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Inscrever, confirmar e cancelar inscrição na newsletter.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/newsletter/services.py::NewsletterService` |
| Teste | `backend/tests/newsletter/test_newsletter_service.py` |

## 3. Contrato

```python
class NewsletterService:
    def __init__(self, session: Session, clock: Clock) -> None:
        self.session = session
        self.clock = clock

    def subscribe(self, email: str) -> NewsletterSubscriber: ...   # idempotente
    def confirm(self, email: str, token: str) -> None: ...
    def unsubscribe(self, email: str) -> None: ...
```

## 4. Comportamento / regras

- `subscribe` idempotente (e-mail já inscrito não duplica).
- Confirmação (double opt-in) marca `confirmed=True`.
- `unsubscribe` define `unsubscribed_at` (não apaga histórico de opt-out).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Subscribe novo | criado |
| T2 | Subscribe repetido | idempotente |
| T3 | Unsubscribe | marca opt-out |

## 6. Rastreabilidade

- RNF-05,06 · Units: `model_subscriber`, `router_newsletter`
