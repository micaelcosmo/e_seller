# Revisão Cíclica (validação de competência · auto-repair · incremento inteligente)

> Trilha self_reflection · e_seller · 2026-06-10 (atualizado: por ÉPICO)
> Roda **ao final de cada ÉPICO** (área/grupo de tarefas). É a "skill" que garante
> qualidade, conserta o que falhou e mantém o backlog vivo — sempre **dentro do
> contexto** (vender e-books).

---

## 0. Quando roda

**Ao concluir um ÉPICO** (um grupo/área de tarefas relacionadas — ex.: *Auth & Contas*,
*Admin*, *Frontend*, *Domínios*), e não a cada task isolada. Durante o épico, as tasks
são marcadas `done` normalmente; a **revisão formal (parecer)** acontece no fechamento
do épico. Re-ancorada na [barra de qualidade](../quality-bar.md).

> Épicos = as áreas do [backlog](../../report/backlog.json) (campo `area`).

## 1. Etapa A — Validação de competência (a task ficou boa?)

Checklist (pontua PASS/FAIL por dimensão):
- [ ] Cumpre o objetivo da task e seus critérios de aceite.
- [ ] **Padrões** ([`../standards/`](../standards/)): POO, classes+DI, sem comprehension/lambda,
      docstrings pt-BR, sem def-in-def/arquivo-só-funções/classe-aninhada.
- [ ] **🚫 Sem dados em hardcode** (config via env; dados externalizados).
- [ ] **Backend:** camadas (router→service→repo), erros tratados, desacoplado.
- [ ] **DB:** relacionamentos determinísticos, constraints, tipos certos, migração + UML.
- [ ] **Frontend:** layout certo (flex/grid), sem reload (fetch), tooltips, a11y, leve.
- [ ] **TDD:** teste antes; Ruff + pytest verdes; cobertura ≥ 95% no domínio.
- [ ] **Spec primeiro:** planning/unit atualizados; STATUS/CHANGELOG/CLAUDE atualizados.

## 2. Etapa B — Auto-repair (se algo falhou)

- Se qualquer item falhar: **não** marca `done`. Cria **sub-tasks de reparo** no backlog
  (ou corrige na hora) e repete a Etapa A até passar.
- Registrar o reparo no [`log.md`](log.md) (honestidade: o que falhou e como foi corrigido).

## 3. Etapa C — Incremento inteligente do backlog

- Procurar trabalho **recém-descoberto** durante a task: edge cases, follow-ups, dívidas,
  testes faltando, integrações pendentes.
- **Adicionar** itens ao backlog (com descrição clara) — respeitando os limites:
  - **mínimo 110**, **máximo 250** itens.
- **Anti-scope-creep (NÃO sair do contexto):** rejeitar qualquer item que não sirva a
  "vender e-books com qualidade". Se não cabe no objetivo, não entra.

## 4. Etapa D — Reportar e seguir

- Atualizar o estado das tasks no `backlog.json` (a página reflete na hora).
- No fechamento do épico, gravar o **parecer** (`review_summary`) e atualizar
  STATUS/CHANGELOG.
- Só então iniciar o **próximo épico**.

## 5. Invariantes

- O backlog é a **fonte de verdade** do que falta/está/concluiu (nunca perder contexto).
- Nenhuma task "pula" a revisão. Nenhuma task sai do objetivo.
- Qualidade > velocidade, mas sempre **funcional e leve**.
