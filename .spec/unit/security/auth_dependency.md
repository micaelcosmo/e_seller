# Unit: get_current_user / require_staff (`dependency`)

> Tipo: `dependency` (FastAPI) · Área: `security`
> Deriva de: ADR-007 · RF-50 · Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Dependency que exige `Bearer <jwt>` válido e resolve o usuário atual (e autorização).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/security/deps.py` (`get_current_user`, `require_staff`) |
| Teste | `backend/tests/security/test_auth_dependency.py` |

## 3. Contrato

```python
def get_current_user(token: str = Depends(oauth2_scheme),
                     jwt: JwtService = Depends(get_jwt_service),
                     session: Session = Depends(get_session)) -> User:
    ...  # 401 se token inválido/expirado; carrega o usuário


def require_staff(user: User = Depends(get_current_user)) -> User:
    ...  # 403 se não for staff
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `jwt_tokens` (`JwtService`) | validar token |
| `accounts/model_admin_user` | carregar usuário |

## 5. Comportamento / regras

- Sem token / inválido / expirado → `401`.
- Usuário inativo → `401`; sem permissão (`require_staff`) → `403`.
- Base para proteger rotas administrativas e (futuro) RBAC.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Token válido | retorna `User` |
| T2 | Sem token | `401` |
| T3 | Token expirado | `401` |
| T4 | Não-staff em `require_staff` | `403` |

## 7. Rastreabilidade

- RF-50 · ADR-007 · Units: `jwt_tokens`, `accounts/router_auth`

## 8. Pendências

- [ ] Integrar com RBAC (`role`) no Tier 🔵.
