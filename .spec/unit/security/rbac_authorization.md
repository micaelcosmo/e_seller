# Unit: RequireRole (`dependency`) — RBAC

> Tipo: `dependency` (classe chamável) · Área: `security` · Tier 🔵
> Deriva de: RF-50 · ADR-007 · Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Autorização baseada em papéis: dependency **chamável** que exige um papel específico.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/security/rbac.py::RequireRole` |
| Teste | `backend/tests/security/test_rbac.py` |

## 3. Contrato

```python
class RequireRole:
    """Dependency chamável que autoriza o acesso por papel (RBAC)."""

    def __init__(self, *allowed: str) -> None:
        self.allowed = allowed

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        """Permite o acesso se o usuário tiver um papel permitido; senão levanta 403."""
        ...
```

> 💡 Usa **classe chamável** (`__call__`), não closure — cumpre "sem `def` dentro de `def`"
> ([`standards/oop-and-naming`](../standards/oop-and-naming.md)). Uso: `Depends(RequireRole("admin"))`.

## 4. Comportamento / regras

- Usa os papéis de [`../backend/accounts/model_role.md`](../backend/accounts/model_role.md).
- Sem papel adequado → `403`.
- Compõe com `get_current_user` ([`auth_dependency`](auth_dependency.md)).
- Comparação de papéis com laço explícito (sem comprehension).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Usuário com papel permitido | acesso |
| T2 | Usuário sem papel | `403` |
| T3 | Sem autenticação | `401` |

## 6. Rastreabilidade

- RF-50 · Units: `auth_dependency`, `accounts/model_role` · Threat model (elevação de privilégio)

## 7. Pendências

- [ ] Permissões finas (além de papéis) — avaliar.
