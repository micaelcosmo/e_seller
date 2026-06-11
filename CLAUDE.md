# CLAUDE.md — e_seller

Guia operacional para qualquer agente (humano ou IA) que trabalhe neste repositório.
Leia este arquivo **antes** de qualquer tarefa.

---

## 1. O que é o projeto

**e_seller** é um portal de vendas de e-books.

- **Backend:** Python + **FastAPI** (Python 3.14.5+), API JSON; SQLAlchemy + Alembic; PostgreSQL.
- **Frontend:** **serviço separado**, tecnologia a ser definida (consome a API do backend).
- **Pagamentos:** Mercado Pago. **Infra:** Docker em todos os serviços.
- **Estado atual:** fase de *planning* — nenhuma linha de código de produção foi escrita ainda.

> O escopo, a stack e a arquitetura detalhada vivem em [`.spec/planning/`](.spec/planning/).
> Este arquivo descreve **como** trabalhamos; o planning descreve **o que** construímos.

---

## 2. Metodologias obrigatórias

Estas regras são **inegociáveis** e se aplicam a **tudo**:

### 2.1 Spec-Driven Development (SDD)
- Nenhuma funcionalidade é implementada sem uma spec correspondente em `.spec/`.
- Fluxo: **Spec → revisão/aprovação → testes → implementação**.
- Toda mudança de comportamento começa atualizando (ou criando) a spec.

### 2.2 Test-Driven Development (TDD)
- Ciclo **Red → Green → Refactor**: escreva o teste que falha, faça passar, refatore.
- Nenhum código de produção é escrito sem um teste que o justifique.
- Cobertura é consequência do processo, não a meta em si.
- **Trilha de testes viva:** [`.spec/unit/tests/`](.spec/unit/tests/) (guias de pytest,
  mock, segurança e I/O) deve ser **atualizada a cada tarefa** que envolva testes, com
  registro no seu próprio `CHANGELOG.md`.

### 2.3 PEP 8 (Python / backend)
- Todo código Python segue [PEP 8](https://peps.python.org/pep-0008/).
- Linter/formatter padrão: **Ruff** (já há `.ruff_cache/` previsto no `.gitignore`).
- Type hints sempre que agregarem clareza.

### 2.4 Padrões de engenharia (OBRIGATÓRIO)
Antes de escrever qualquer código, ler [`.spec/standards/`](.spec/standards/). Em resumo:
- **SOLID** sempre; **POO** (sem variáveis globais; atributos via `self.` no `__init__`).
- **Services = classes** com injeção de dependência no construtor.
- **Laços `for` explícitos** — proibido list/dict comprehension e `lambda`.
- **Nomenclatura declarativa** (`produto`, nunca `prod_x`).
- **Código em inglês; docstrings/comentários em pt-BR** (UTF-8). **Docstring em TODA funcionalidade.**
- **Sem `def` dentro de `def`**, **sem arquivo só com funções** (use classe/`__call__`), **sem classe dentro de classe**.
  - Exceção mínima: handlers/dependencies do FastAPI podem ser funções finas que só delegam (com docstring).
- **🚫 SEM DADOS EM HARDCODE:** config/segredos/valores via env (`Settings`); dados via DB/seed externalizado.
- Imports na **hierarquia** correta (stdlib → terceiros → locais, com linha em branco).
- Python **3.14.5+**; enforcement por Ruff + pre-commit + revisão de PR.

### 2.5 Barra de qualidade e revisão cíclica (OBRIGATÓRIO)
- **Barra de qualidade:** [`.spec/quality-bar.md`](.spec/quality-bar.md) — backend POO sem amarras,
  DB determinístico/observável, frontend UX correta (centralização certa, tooltips, sem reload).
- **Revisão cíclica** ao final de **cada épico** (área de tarefas): [`.spec/self_reflection/cyclic-review.md`](.spec/self_reflection/cyclic-review.md)
  (valida competência → auto-repair → incrementa backlog). Backlog mantido entre **110 e 250** itens.
- **NÃO sair do contexto:** tudo serve a "vender e-books"; rejeitar trabalho fora do objetivo.
- **Fonte de verdade do progresso:** [`report/backlog.json`](report/backlog.json) (alimenta a página de relatório).

---

## 3. Estrutura de documentação

| Arquivo | Propósito |
|---|---|
| `CLAUDE.md` | Como trabalhamos (este arquivo). |
| `STATUS.md` | Onde estamos agora — fase atual, próximos passos, pendências. |
| `CHANGELOG.md` | Histórico de mudanças em `STATUS.md` e `CLAUDE.md`. |
| `.spec/` | Todas as especificações do projeto. |
| `.spec/planning/` | Planejamento (fase concluída e congelada). |
| `.spec/standards/` | Padrões de engenharia (vivos, obrigatórios) — ler antes de codar. |
| `.spec/unit/` | Specs de unidade por componente (**fase atual**). |
| `.spec/api/` | Contrato da API (OpenAPI como fonte da verdade) — vivo. |
| `.spec/ops/` | Runbooks operacionais (deploy, backup, segredos, LGPD, incidente) — vivo. |
| `.spec/observability/` | Logs, métricas, alertas, tracing — vivo. |
| `.spec/security/` | Threat model (STRIDE) em nível de sistema — vivo. |
| `.spec/dashboard/` | Dashboard de evolução do projeto (métricas/gráficos) — vivo. |
| `.spec/distribution/` | Distribuição/acesso (Cloudflare Tunnel, PC-as-server) — vivo. |
| `.spec/frontend/` | Frontends: storefront (Next.js/SSR) + dashboard-ui — vivo. |
| `.spec/self_reflection/` | Prática de auto-revisão do código pelo agente — vivo. |
| `.spec/flowcharts/` | Fluxogramas (dev, backend, frontend, navegação cliente/admin) — vivo. |
| `.spec/roadmap.md` | Roadmap vivo (sequenciamento por marcos/tiers). |
| `.spec/checklist.md` | Checklist mestre do projeto (vivo). |

> **UML do DB:** [`.spec/unit/db/uml-class-diagram.md`](.spec/unit/db/uml-class-diagram.md)
> deve ser atualizado **a cada migração** (junto da migration Alembic).
> **Portas não-padrão** (base 48xxx): ver [`.spec/unit/infra/ports.md`](.spec/unit/infra/ports.md).

> Trilhas **vivas** (standards, api, ops, observability, security, unit/tests) têm
> `CHANGELOG.md` próprio e devem ser atualizadas a cada tarefa pertinente.

---

## 4. Regra de ouro da fase atual

> **Fase atual: especificação de unidades.** Trabalhamos exclusivamente dentro de
> [`.spec/unit/`](.spec/unit/). Não criar código de produção ainda.
>
> O [planning](.spec/planning/) está completo e aprovado (fase anterior, congelada).
> Cada unit spec deriva de um ponto do planning e lista seus casos de teste (base do TDD).

---

## 5. Convenções

- **Idioma:** documentação e comunicação em **português (pt-BR)**.
- **Datas:** sempre absolutas (ex.: `2026-06-06`), nunca relativas.
- **Commits:** descritivos; referenciar a spec relacionada quando aplicável.
- **Atualização de status:** ao concluir um marco, atualizar `STATUS.md` e registrar em `CHANGELOG.md`.
