# Unit: AdminAuth (`admin`)

> Tipo: `admin` auth · Área: `backend/admin`
> Deriva de: RF-50 · ADR-007/008 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Backend de autenticação do painel SQLAdmin (login do operador P2).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/admin/auth.py::AdminAuth` |
| Teste | `backend/tests/admin/test_admin_auth.py` |

## 3. Contrato

```python
class AdminAuth(AuthenticationBackend):
    def __init__(self, authenticator: Authenticator) -> None:
        self.authenticator = authenticator

    async def login(self, request) -> bool: ...     # valida credenciais (staff)
    async def logout(self, request) -> bool: ...
    async def authenticate(self, request) -> bool: ...  # checa sessão/token
```

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `accounts/service_authenticate` | validar credenciais | real/fake |
| `accounts/model_admin_user` (`is_staff`) | autorizar acesso | real |

## 5. Comportamento / regras

- Só usuários com `is_staff` (ou role admin/staff no Tier 🔵) acessam o painel.
- Reusa o `Authenticator` (sem duplicar lógica de senha).
- Sessão protegida; logout limpa a sessão.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Staff com senha correta | login ok |
| T2 | Usuário sem `is_staff` | acesso negado |
| T3 | Senha errada | login falha |

## 7. Rastreabilidade

- RF-50 · ADR-007/008 · Units: `accounts/service_authenticate`, `sqladmin_setup`

## 8. Pendências

- [ ] Sessão por cookie seguro vs token no painel.
