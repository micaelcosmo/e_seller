# Plano do Dashboard de Evolução

> Trilha dashboard · e_seller · 2026-06-07 · Status: **Rascunho**

---

## 1. Para quem e para quê

Para o **Micael** (dono do projeto) acompanhar a evolução de ponta a ponta: o que já
foi feito, o que falta, decisões tomadas e saúde do projeto — sem ler todos os docs.

## 2. Painéis e gráficos (pontos principais)

| Painel | Gráfico | Mede |
|---|---|---|
| **Objetivos** | cartões/checklist | objetivos do produto ([`../planning/01-visao-de-produto.md`](../planning/01-visao-de-produto.md)) e status |
| **Progresso de specs** | barras/donut | nº de unit specs por área e % concluído |
| **Progresso de marcos** | timeline/gantt | M0…M16 ([`../roadmap.md`](../roadmap.md)): planejado vs. feito |
| **Cobertura/Qualidade** | linha | cobertura de testes ao longo do tempo (quando houver código) |
| **Decisões (ADR)** | log/tabela | decisões e data ([`../planning/07-adr-stack.md`](../planning/07-adr-stack.md), ADRs futuros) |
| **Riscos** | matriz (impacto×prob.) | [`../planning/22-matriz-de-riscos.md`](../planning/22-matriz-de-riscos.md) |
| **KPIs do produto** | indicadores | conversão, entrega, etc. (quando em produção — [`../observability/metrics.md`](../observability/metrics.md)) |
| **Atividade** | heatmap/linha | commits/mudanças de spec por período (git) |

## 3. Fontes de dados

- `STATUS.md`, `CHANGELOG.md` (raiz e por trilha) — estado e histórico.
- `.spec/roadmap.md` — marcos.
- Contagem de arquivos em `.spec/unit/**` — progresso de specs.
- Git (commits, datas) — atividade.
- Relatórios de cobertura do CI — qualidade (fase de código).
- Métricas de runtime (observability) — KPIs (produção).

> 💡 Os dados são **derivados de artefatos que já mantemos** — o dashboard não cria
> uma fonte paralela de verdade; ele **agrega** o que `STATUS`/`CHANGELOG`/specs/git já dizem.

## 4. Como é atualizado (cadência)

- **Antes** de um desenvolvimento: atualizar objetivos/escopo do marco.
- **Durante:** progresso de specs/tarefas.
- **Depois:** marcos concluídos, decisões, cobertura, CHANGELOG.
- Idealmente, um **gerador** lê os artefatos e produz os dados do dashboard
  (script no backend), evitando trabalho manual — ver tech abaixo.

## 5. Tecnologia (proposta)

- **Dados:** um endpoint/JSON gerado a partir dos artefatos (ex.: `GET /dashboard/data`
  no backend, ou um arquivo `dashboard.json` gerado no CI).
- **Render (self_reflection):** frontend simples com biblioteca de gráficos
  (ex.: Chart.js/Recharts) — a decidir junto com a stack de frontend.
- **Custo zero**, open-source.

## 6. Pendências

- [ ] Gerador automático (script) vs atualização manual no início.
- [ ] Onde hospedar o dashboard (porta `48088` — ver [`../unit/infra/ports.md`](../unit/infra/ports.md)).
- [ ] Definir junto com a stack de frontend (self_reflection).
