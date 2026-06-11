# Unit: router_newsletter (`router`)

> Tipo: `router` · Área: `backend/newsletter` · Tier 🔵
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Endpoints públicos de inscrição/confirmação/cancelamento.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/newsletter/router.py` |
| Teste | `backend/tests/newsletter/test_router_newsletter.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/v1/newsletter", tags=["newsletter"])

@router.post("/subscribe", status_code=202)
def subscribe(data: SubscribeIn, svc: NewsletterService = Depends(...)): ...

@router.get("/confirm")      # link do e-mail (email + token)
def confirm(email: EmailStr, token: str, svc: NewsletterService = Depends(...)): ...

@router.post("/unsubscribe", status_code=202)
def unsubscribe(data: SubscribeIn, svc: NewsletterService = Depends(...)): ...
```

## 4. Comportamento / regras

- `202` para subscribe/unsubscribe (assíncrono conceitualmente).
- `EmailStr` valida o e-mail (`422` se inválido).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Subscribe válido | `202` |
| T2 | E-mail inválido | `422` |
| T3 | Unsubscribe | `202` |

## 6. Rastreabilidade

- Units: `service_newsletter` · API [`endpoints`](../../../api/endpoints.md)
