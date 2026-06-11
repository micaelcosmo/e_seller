# Unit: User (`model`)

> Tipo: `model` · Área: `backend/accounts`
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) · RF-50 · ADR-007 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Mapear `user` (conta). No MVP cobre o admin; preparado para clientes e RBAC.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/accounts/models.py::User` |
| Teste | `backend/tests/accounts/test_model_user.py` |

## 3. Contrato

```python
class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(160), default="")
    is_active: Mapped[bool] = mapped_column(default=True)
    is_staff: Mapped[bool] = mapped_column(default=False)   # acesso ao admin (até RBAC entrar)
    created_at: Mapped[datetime]
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/db_session` (Base) | mapeamento |

## 5. Comportamento / regras

- `email` único.
- `password_hash` nunca guarda senha em claro (hash em [`security/password_hashing`](../../security/README.md)).
- `is_staff` libera o painel admin no MVP; migra para `role`/`user_role` (RBAC) no Tier 🔵.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Criar usuário | persiste; `is_active=True` |
| T2 | E-mail duplicado | viola UNIQUE |

## 7. Rastreabilidade

- RF-50 · ADR-007 · Units: `service_authenticate`, `security/password_hashing`, RBAC (`role`/`user_role` futuras)

## 8. Pendências

- [ ] Quando introduzir `role`/`user_role` (RBAC confirmado).
