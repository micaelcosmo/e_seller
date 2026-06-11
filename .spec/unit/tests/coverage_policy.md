# Unit: coverage_policy (`tests`)

> Tipo: `tests`/política · Área: `tests`
> Deriva de: [`planning/13`](../../planning/13-estrategia-de-testes.md), [`15`](../../planning/15-ci-cd.md) · RNF-31 ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Definir a política de cobertura e o gate no CI.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/pyproject.toml` (`[tool.coverage.report] fail_under`) + CI |

## 3. Contrato

- **`fail_under = 95`** (decidido em 2026-06-07) — gate de cobertura no CI.
- Relatório `term-missing` + artefato no CI.

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `pytest-cov` | medir |
| `infra/ci_pipeline` | aplicar o gate |

## 5. Comportamento / regras

- Cobertura é **consequência do TDD**, não meta cega.
- CI **falha** abaixo do limite.
- Foco: pagamento, entrega, estados, segurança.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | Cobertura < limite | CI falha |
| T2 | Relatório | mostra linhas não cobertas |

## 7. Rastreabilidade

- RNF-31 · Planning [`13`](../../planning/13-estrategia-de-testes.md), [`15`](../../planning/15-ci-cd.md) · Units: `pytest_config`, `ci_pipeline`

## 8. Pendências

- [x] Limite definitivo: **95%** (CI falha abaixo disso).
