# Unit: JwtService (`security`)

> Tipo: `security` · Área: `security`
> Deriva de: ADR-007 ([`planning/07`](../../planning/07-adr-stack.md)) · RF-50 ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Gerar e validar JWTs (autenticação stateless do admin/API).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/security/jwt.py::JwtService` |
| Teste | `backend/tests/security/test_jwt.py` |

## 3. Contrato

```python
class JwtService:
    def __init__(self, secret_key: str, clock: Clock, ttl_minutes: int = 60) -> None:
        self.secret_key = secret_key
        self.clock = clock
        self.ttl_minutes = ttl_minutes

    def issue(self, subject: str) -> str: ...
    def verify(self, token: str) -> TokenClaims:
        ...  # levanta InvalidToken | ExpiredToken
```

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| lib JWT (ex.: `pyjwt`) | assinar/verificar | real |
| `clock` | expiração | injetado/freezegun |
| `core/config.app_secret_key` | chave | injetado |

## 5. Comportamento / regras

- Algoritmo simétrico (HS256) com `app_secret_key`.
- Inclui `exp`; expira após `ttl_minutes`.
- Token adulterado/expirado → exceção (nunca aceitar).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | issue + verify | claims corretos |
| T2 | Token expirado (tempo avançado) | `ExpiredToken` |
| T3 | Assinatura adulterada | `InvalidToken` |

## 7. Rastreabilidade

- ADR-007 · RF-50 · Units: `accounts/service_authenticate`, `auth_dependency`

## 8. Pendências

- [ ] Refresh token (Tier 🔵); rotação de chave.
