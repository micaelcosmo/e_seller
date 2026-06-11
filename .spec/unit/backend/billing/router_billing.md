# Unit: router_billing (`router`)

> Tipo: `router` · Área: `backend/billing` · Tier 🔵
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Gerenciar perfil fiscal do usuário (e consultar NF, quando integrado).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/billing/router.py` |
| Teste | `backend/tests/billing/test_router_billing.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

@router.put("/profile", response_model=BillingProfileOut)
def upsert_profile(data: BillingProfileIn, user: User = Depends(get_current_user),
                   svc: BillingService = Depends(...)): ...
```

## 4. Comportamento / regras

- Exige login (`401`); `422` para CPF/CNPJ inválido.
- Emissão de NF é acionada internamente (pós-pagamento), não exposta como ação pública direta no MVP.

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Upsert válido | `200` |
| T2 | Sem login | `401` |
| T3 | CPF inválido | `422` |

## 6. Rastreabilidade

- Units: `service_billing`, `security/auth_dependency` · API [`endpoints`](../../../api/endpoints.md)
