# Unit: Authenticator (`service`)

> Tipo: `service` · Área: `backend/accounts`
> Deriva de: RF-50 · ADR-007 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Autenticar um usuário por e-mail/senha e emitir um JWT.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/accounts/services.py::Authenticator` |
| Teste | `backend/tests/accounts/test_authenticate.py` |

## 3. Contrato

```python
class Authenticator:
    def __init__(self, session: Session, hasher: PasswordHasher, tokens: JwtService) -> None:
        self.session = session
        self.hasher = hasher
        self.tokens = tokens

    def login(self, email: str, password: str) -> str:
        ...  # retorna JWT; levanta InvalidCredentials
```

- **Saída:** JWT (string).
- **Erros:** `InvalidCredentials` (401) — mensagem genérica.

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `session` / `model_admin_user` | buscar usuário | real |
| `security/password_hashing` (`PasswordHasher`) | verificar senha | real/fake |
| `security/jwt_tokens` (`JwtService`) | emitir token | real/fake |

## 5. Comportamento / regras

- Usuário inexistente **ou** senha errada → `InvalidCredentials` (não revelar qual).
- Usuário inativo → `InvalidCredentials`.
- Não loga senha nem hash.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Credenciais corretas | retorna JWT válido |
| T2 | Senha errada | `InvalidCredentials` |
| T3 | E-mail inexistente | `InvalidCredentials` |
| T4 | Usuário inativo | `InvalidCredentials` |

## 7. Rastreabilidade

- RF-50 · ADR-007 · Units: `router_auth`, `security/jwt_tokens`, `security/password_hashing`

## 8. Pendências

- [ ] Bloqueio por tentativas (rate limit) — futuro.
