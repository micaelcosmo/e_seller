# Unit: router_auth (`router`)

> Tipo: `router` · Área: `backend/accounts`
> Deriva de: [`planning/11`](../../../planning/11-contratos-api.md) §6 · RF-50 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Expor `POST /api/auth/token` (OAuth2 password flow) retornando JWT.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/accounts/router.py` |
| Teste | `backend/tests/accounts/test_router_auth.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(),
          auth: Authenticator = Depends(get_authenticator)) -> TokenOut:
    token = auth.login(form.username, form.password)
    return TokenOut(access_token=token, token_type="bearer")
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `service_authenticate` | autenticar |
| `schema TokenOut` | resposta |

## 5. Comportamento / regras

- `200` com `access_token` em sucesso; `401` em `InvalidCredentials`.
- Form padrão OAuth2 (`username`=e-mail, `password`).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Login correto | `200` com `access_token` |
| T2 | Login inválido | `401` |

## 7. Rastreabilidade

- RF-50 · Units: `service_authenticate`, `security/auth_dependency`

## 8. Pendências

- [ ] Refresh token (Tier 🔵).
