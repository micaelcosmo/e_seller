# Unit: conftest_db (`tests`/fixture)

> Tipo: `fixture` · Área: `tests`
> Deriva de: [`planning/13`](../../planning/13-estrategia-de-testes.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Fixture de sessão SQLAlchemy de teste, com **transação revertida** por teste (isolamento).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/tests/conftest.py` (`db_session`) |

## 3. Contrato

```python
@pytest.fixture
def db_session() -> Iterator[Session]:
    # cria schema/usa DB de teste; abre transação; yield; rollback ao final
    ...
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/db_session` | engine/sessão |
| Postgres de teste | banco real efêmero (CI) |

## 5. Comportamento / regras

- Cada teste roda em transação revertida → sem vazamento entre testes.
- Banco efêmero no CI (ver [`infra/ci_pipeline`](../infra/README.md)).

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | Inserção em teste A | não aparece no teste B |
| T2 | Rollback | estado limpo após cada teste |

## 7. Rastreabilidade

- Planning [`13`](../../planning/13-estrategia-de-testes.md) · Units: `conftest_client`, `factories`

## 8. Pendências

- [ ] Estratégia: transação aninhada (savepoint) vs recriar schema.
