# .spec/dashboard/

Trilha **viva** do **Dashboard de Evolução do Projeto** — a "observabilidade do
projeto" (diferente de [`../observability/`](../observability/), que é do *app* em runtime).

> Objetivo: visualizar, com **gráficos**, como o e_seller evolui — objetivos, métricas,
> decisões, progresso por marco, riscos — atualizado **antes/durante/depois** de cada
> desenvolvimento, no mesmo espírito de `CLAUDE.md`/`STATUS.md`.

## Documentos

| Doc | Assunto |
|---|---|
| [`plan.md`](plan.md) | O que o dashboard mostra, gráficos, fontes de dados, cadência, tech. |
| [`metrics.md`](metrics.md) | Catálogo de métricas de evolução do projeto. |

## Relação com o frontend (dashboard-ui)

O **dashboard** (esta trilha) define **o quê** mostrar e **de onde** vêm os dados.
A UI que **renderiza** os gráficos é o **dashboard-ui** ([`../frontend/dashboard-ui.md`](../frontend/dashboard-ui.md)).

> Obs.: `self_reflection` é a prática de auto-revisão do código pelo agente
> ([`../self_reflection/`](../self_reflection/)) — não confundir com este dashboard.

## Regra de manutenção (constante)

Atualizar este dashboard **a cada update do projeto** (antes/durante/depois), junto
com `STATUS.md`/`CHANGELOG.md`, e registrar em [`CHANGELOG.md`](CHANGELOG.md).
