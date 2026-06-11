# Unit: time_control (`tests`/fixture)

> Tipo: `fixture` · Área: `tests`
> Deriva de: [`planning/13`](../../planning/13-estrategia-de-testes.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Controlar o tempo nos testes (expiração de grants, JWT) de forma determinística.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/tests/conftest.py` (fixture de clock) / uso de `freezegun` |

## 3. Contrato

```python
@pytest.fixture
def frozen_clock():
    # injeta um Clock fixo OU usa freezegun para congelar/avançar o tempo
    ...
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `freezegun` (ou `Clock` injetável) | tempo determinístico |

## 5. Comportamento / regras

- Preferir **`Clock` injetável** (DIP) onde possível; `freezegun` como complemento.
- Permite avançar o tempo para testar expiração.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | Avançar além do `expires_at` | grant expira |
| T2 | JWT após `ttl` | token expira |

## 7. Rastreabilidade

- Planning [`13`](../../planning/13-estrategia-de-testes.md) · Units: `delivery/service_validate_grant`, `security/jwt_tokens`

## 8. Pendências

- [ ] Padronizar `Clock` injetável em todos os services com tempo.
