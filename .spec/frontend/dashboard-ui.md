# Dashboard UI (evolução do projeto)

> Trilha frontend · e_seller · 2026-06-07 · Status: **Rascunho**
> Renderiza os dados definidos em [`../dashboard/`](../dashboard/).

---

## 1. Objetivo

UI com **gráficos** da evolução do projeto (objetivos, progresso de specs/marcos,
decisões, riscos), atualizada constantemente.

## 2. Fonte de dados

- `dashboard.json` gerado a partir dos artefatos (`STATUS.md`, `CHANGELOG`s, `roadmap.md`,
  contagem de specs, git) — ver [`../dashboard/plan.md`](../dashboard/plan.md).
- (Futuro) `GET /dashboard/data` no backend.

## 3. Painéis (gráficos)

| Painel | Gráfico (Recharts/Chart.js) |
|---|---|
| Objetivos | cartões/checklist |
| Progresso de specs | barras/donut (por área) |
| Marcos (roadmap) | timeline/gantt |
| Decisões | tabela/log |
| Riscos | matriz impacto×prob. |
| Cobertura (fase código) | linha temporal |

## 4. Acesso

- Porta **48088** (não-padrão); rota protegida (não público) — é ferramenta interna.
- Não expor pelo túnel público sem proteção ([`../distribution/cloudflare-tunnel.md`](../distribution/cloudflare-tunnel.md)).

## 5. Pendências

- [ ] Recharts vs Chart.js.
- [ ] Gerador do `dashboard.json` (script) — ver dashboard/plan §4.
- [ ] App próprio vs rota `/dashboard` no mesmo Next.
