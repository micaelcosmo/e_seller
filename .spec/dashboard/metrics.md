# Métricas de Evolução do Projeto

> Trilha dashboard · e_seller · 2026-06-07
> Métricas **do projeto** (não do app em runtime — essas estão em [`../observability/metrics.md`](../observability/metrics.md)).

---

## 1. Progresso de especificação

| Métrica | Como calcular |
|---|---|
| Unit specs por área | contagem de `.md` em `.spec/unit/<área>/` |
| Specs totais | total de unit specs (~100 hoje) |
| Trilhas vivas | nº de trilhas com CHANGELOG atualizado |

## 2. Progresso de implementação (fase de código)

| Métrica | Fonte |
|---|---|
| Marcos concluídos | `roadmap.md` (M0…M16) |
| Cobertura de testes | relatório do CI |
| Itens "Must" entregues | RF/US marcados |
| Bugs abertos/fechados | issues/changelog |

## 3. Decisões e riscos

| Métrica | Fonte |
|---|---|
| Decisões registradas | ADRs |
| Decisões em aberto | pendências em STATUS/specs |
| Riscos por severidade | `planning/22-matriz-de-riscos.md` |

## 4. Atividade

| Métrica | Fonte |
|---|---|
| Commits por período | git |
| Mudanças de spec por período | git (paths em `.spec/`) |

## 5. Snapshot atual (manual — 2026-06-07, noite)

- Specs: planning (22) · standards (8) · unit (~135) · trilhas vivas: api, ops,
  observability, security, dashboard, distribution, frontend, self_reflection.
- **Código:** backend MVP implementado (FastAPI/SQLite) — **22 testes verdes**, Ruff ok.
- **Deploy:** no ar via uvicorn `:48080` + Cloudflare quick tunnel (URL temporária).
- Marcos: M0–M5 (MVP) essencialmente cobertos em código (auth/admin/Alembic pendentes).

> Snapshot manual; será substituído por dados gerados automaticamente (ver plan.md §4).
