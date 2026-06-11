# Unit: setup_admin (`admin`)

> Tipo: `admin` (SQLAdmin) · Área: `backend/admin`
> Deriva de: [`planning/07`](../../../planning/07-adr-stack.md) ADR-008 · [`11`](../../../planning/11-contratos-api.md) §7 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Montar o painel **SQLAdmin** no app FastAPI e registrar as views administrativas.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/admin/setup.py::setup_admin` |
| Teste | `backend/tests/admin/test_sqladmin_setup.py` |

## 3. Contrato

```python
def setup_admin(app: FastAPI, engine: Engine, auth_backend: AdminAuth) -> Admin:
    admin = Admin(app, engine, authentication_backend=auth_backend)
    admin.add_view(ProductAdmin)
    admin.add_view(OrderAdmin)
    # ... demais views
    return admin
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `sqladmin` | painel | 
| `admin_views_*` | views CRUD |
| `admin_auth_backend` | login do painel |
| `core/db_session` (engine) | acesso a dados |

## 5. Comportamento / regras

- Montado em `create_app` (ver [`core/app_factory`](../core/app_factory.md)).
- Exige autenticação (sem painel aberto).
- Rota base típica: `/admin`.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Admin montado | rota `/admin` existe |
| T2 | Acesso sem login | redireciona/401 |

## 7. Rastreabilidade

- ADR-008 · Units: `admin_views_product`, `admin_views_order`, `admin_auth_backend`

## 8. Pendências

- [ ] Confirmar compatibilidade SQLAdmin × versão do SQLAlchemy/FastAPI.
