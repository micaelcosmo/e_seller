# Unit: ci_pipeline (`infra`)

> Tipo: `infra` · Área: `infra`
> Deriva de: [`planning/15`](../../planning/15-ci-cd.md), [`standards/enforcement`](../../standards/enforcement.md) ·
> RNF-30,31 · Status: **Rascunho**

---

## 1. Objetivo

Pipeline de CI que bloqueia merge com código fora do padrão ou com testes falhando.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `.github/workflows/ci.yml` (ou equivalente) |
| Teste | execução do próprio CI |

## 3. Conteúdo (contrato)

1. checkout
2. setup Python 3.14.x (ou imagem do projeto)
3. instalar deps (cacheadas, via lockfile)
4. `ruff check` + `ruff format --check`
5. subir **Postgres** de serviço (efêmero) — testes com asyncpg
6. `pytest` + cobertura
7. **falhar se cobertura < 95%**

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `ruff_config` | regras de estilo |
| `tests/*` | suíte e cobertura |
| `db` (serviço) | testes de integração |

## 5. Comportamento / regras

- Gates: Ruff, testes e cobertura (ver [`planning/15`](../../planning/15-ci-cd.md)).
- pre-commit cobre o mesmo localmente (ver [`standards/enforcement`](../../standards/enforcement.md)).
- (opcional) scan de segredos.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | PR com lint quebrado | CI falha |
| T2 | PR com teste quebrado | CI falha |
| T3 | PR verde | merge liberado |

## 7. Rastreabilidade

- RNF-30,31 · Planning [`15`](../../planning/15-ci-cd.md) · Units: `ruff_config`, `tests/coverage_policy`

## 8. Decisões (2026-06-07)

- **Plataforma: GitHub Actions** (gratuito p/ o repositório).
- **Gate de cobertura: 95%**.
- Deploy de baixo custo: **PC como servidor + Cloudflare Tunnel** por ora
  ([`../../distribution/`](../../distribution/)); hospedagem gratuita/barata a avaliar depois.
