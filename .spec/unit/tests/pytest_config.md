# Unit: pytest_config (`tests`)

> Tipo: `tests`/config · Área: `tests`
> Deriva de: [`planning/13`](../../planning/13-estrategia-de-testes.md) · RNF-31 ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Configurar o pytest (asyncio, cobertura, descoberta) no projeto.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.coverage.*]`) |

## 3. Conteúdo (contrato)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "--cov=app --cov-report=term-missing"
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `pytest`, `pytest-asyncio`, `pytest-cov` | runner/cobertura |

## 5. Comportamento / regras

- `asyncio_mode=auto` para testes async sem boilerplate.
- Cobertura medida sobre `app`.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | `pytest` | descobre e roda os testes |
| T2 | Relatório de cobertura | gerado |

## 7. Rastreabilidade

- RNF-31 · Planning [`13`](../../planning/13-estrategia-de-testes.md) · Units: `coverage_policy`, `conftest_*`

## 8. Pendências

- [ ] Marcadores (`unit`, `integration`, `e2e`).
