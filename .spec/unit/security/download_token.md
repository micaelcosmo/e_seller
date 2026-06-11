# Unit: TokenFactory (`security`)

> Tipo: `security` · Área: `security`
> Deriva de: RF-30 · [`planning/20`](../../planning/20-entrega-ebook-anti-pirataria.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Gerar tokens de download **criptograficamente seguros**, únicos e imprevisíveis.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/security/tokens.py::TokenFactory` |
| Teste | `backend/tests/security/test_download_token.py` |

## 3. Contrato

```python
class TokenFactory:
    def __init__(self, n_bytes: int = 32) -> None:
        self.n_bytes = n_bytes

    def generate(self) -> str:
        return secrets.token_urlsafe(self.n_bytes)
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `secrets` (stdlib) | aleatoriedade segura |

## 5. Comportamento / regras

- Usa `secrets` (não `random`).
- Token longo (≥ 32 bytes), URL-safe.
- Unicidade garantida pela coluna UNIQUE; colisão é improvável.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | generate | string não vazia, URL-safe |
| T2 | dois generate | tokens diferentes |
| T3 | comprimento | compatível com `n_bytes` |

## 7. Rastreabilidade

- RF-30 · Units: `delivery/service_issue_download`, `delivery/model_download_grant`

## 8. Pendências

- [ ] Em testes, injetar um `TokenFactory` determinístico (fake).
