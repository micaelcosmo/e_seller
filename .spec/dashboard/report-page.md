# Spec — Página de Relatório de Execução

> Trilha dashboard · e_seller · 2026-06-10 · Status: **Vivo**
> Serviço `report/` (separado do app), monitorável por link próprio. Lê o
> [`backlog.json`](../../report/backlog.json) e renderiza o estado das tarefas.

---

## 1. Objetivo

Painel **descritivo** para o Micael acompanhar **só por ele**: o que está no backlog,
o que está em execução e o que foi concluído — além do **parecer da skill validadora**
(revisão cíclica) e **data/hora de Brasília**.

## 2. Requisitos

- **Estados:** seções A fazer / Em execução / Concluído / Bloqueado, com contadores e
  barra de progresso.
- **Data e hora — Brasília (GMT-3):** exibir o horário atual (relógio que atualiza a
  cada segundo) e o "atualizado em" do servidor; Brasil não tem horário de verão → UTC-3 fixo.
- **Parecer da skill validadora:** um painel com o veredito da [revisão cíclica](../self_reflection/cyclic-review.md)
  (passou/auto-repair/itens incrementados) e, por tarefa concluída, uma nota de parecer.
- **Auto-refresh** (~20s) + relógio JS ao vivo.
- **Sem hardcode:** caminho do backlog via env `BACKLOG_PATH`; dados vêm do JSON.

## 3. Dados (backlog.json)

- `tasks[]`: `id, area, title, desc, state, note?, review?`.
- `review?` por tarefa: `{ verdict: "ok|repair", note }`.
- `review_summary`: `{ last, verdict, repaired, added, note }` — parecer global.
- `links`: `{ app, report }`.

## 4. Implementação

- `BacklogReader` (lê JSON) + `ReportRenderer` (monta HTML) + `router` (FastAPI).
- Hora de Brasília calculada server-side (UTC-3) e também por relógio JS no cliente.
- Render do parecer global (painel) e por-tarefa (cartão concluído).

## 5. Pendências

- [ ] (futuro) gráficos da evolução (dashboard-ui) consumindo os mesmos dados.
