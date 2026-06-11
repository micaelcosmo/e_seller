# Unit: Role / UserRole (`model`) — RBAC

> Tipo: `model` · Área: `backend/accounts` · Tier 🔵
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) · RF-50 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Mapear papéis (RBAC): `role` e a associação `user_role` (N:N).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/accounts/models.py` (`Role`, `UserRole`) |
| Teste | `backend/tests/accounts/test_model_role.py` |

## 3. Contrato

```python
class Role(Base):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True)  # admin|staff|author|customer


class UserRole(Base):
    __tablename__ = "user_role"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)
```

## 4. Comportamento / regras

- `role.name` único; conjunto inicial: admin, staff, author, customer.
- Substitui o `is_staff` simples do MVP (que permanece até a migração).
- Autorização consome isto via [`../../security/rbac_authorization.md`](../../security/rbac_authorization.md).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Atribuir papel a usuário | associação criada |
| T2 | Papel duplicado | viola UNIQUE |
| T3 | Usuário com vários papéis | todos resolvidos |

## 6. Rastreabilidade

- RF-50 · Units: `model_admin_user`, `security/rbac_authorization`

## 7. Pendências

- [ ] Migrar `is_staff` → papéis; seed dos papéis.
