# Unit: PasswordHasher (`security`)

> Tipo: `security` · Área: `security`
> Deriva de: ADR-007 · RNF (segurança) · Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Hash e verificação de senha (nunca armazenar senha em claro).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/security/passwords.py::PasswordHasher` |
| Teste | `backend/tests/security/test_passwords.py` |

## 3. Contrato

```python
class PasswordHasher:
    def hash(self, plain: str) -> str: ...
    def verify(self, plain: str, hashed: str) -> bool: ...
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| lib de hashing (bcrypt/argon2, ex.: `passlib`/`pwdlib`) | derivar/verificar |

## 5. Comportamento / regras

- Algoritmo forte com salt (bcrypt ou argon2).
- `verify` resistente a timing (comparação da própria lib).
- Nunca logar senha/hash.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | hash + verify correto | `True` |
| T2 | senha errada | `False` |
| T3 | dois hashes da mesma senha | diferentes (salt) |

## 7. Rastreabilidade

- ADR-007 · Units: `accounts/service_authenticate`, `db/seeds`

## 8. Pendências

- [ ] Escolher bcrypt vs argon2 (parâmetros de custo).
