# Unit: ruff_config (`infra`)

> Tipo: `infra` · Área: `infra`
> Deriva de: [`standards/python-and-tooling`](../../standards/python-and-tooling.md), [`pep8-and-imports`](../../standards/pep8-and-imports.md) ·
> RNF-30 · Status: **Rascunho**

---

## 1. Objetivo

Configurar o Ruff (lint + format) refletindo os padrões — e **sem** habilitar `C4`.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/pyproject.toml` (`[tool.ruff]`) |
| Teste | CI: `ruff check` + `ruff format --check` |

## 3. Conteúdo (contrato)

```toml
[tool.ruff]
line-length = 88
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "ASYNC", "N", "PL"]
# NÃO incluir "C4": ela incentiva comprehensions, o que viola oop-and-naming.

[tool.ruff.format]
quote-style = "double"
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `standards/*` | regras que devem ser refletidas |
| `ci_pipeline` | execução |

## 5. Comportamento / regras

- `I` aplica a hierarquia de imports.
- `N` cobre nomenclatura básica.
- A proibição de comprehension/lambda **não** é coberta pelo Ruff → revisão de PR.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | Código fora do PEP8 | `ruff check` falha |
| T2 | Imports fora de ordem | `ruff` reordena/aponta |
| T3 | `C4` não habilitado | comprehensions não são "sugeridas" |

## 7. Rastreabilidade

- RNF-30 · Standards · Units: `ci_pipeline`, `tests/*`

## 8. Pendências

- [ ] Considerar `mypy` no futuro.
