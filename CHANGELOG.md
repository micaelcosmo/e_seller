# CHANGELOG.md — e_seller

> Histórico de mudanças em `STATUS.md` e `CLAUDE.md`.
> Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
> Datas no formato `AAAA-MM-DD`.

---

## [Não lançado]

### 2026-06-13 — Branch enrichment: análise, roadmap e planning

- **Branch `enrichment`** criada de `main` (HEAD `96ca46f`).
- **STATUS.md** atualizado: fase Enrichment; novos épicos DOC/AAA/FEV/DBE/BEE registrados.
- **`.spec/roadmap.md`** reescrito: reflete estado MVP completo + roadmap de enrichment.
- **`.spec/enrichment/`** criado: 4 docs de planning (AAA, Frontend, DB, Backend).
- **`.spec/tests/`** criado: specs YAML adversariais por tópico.
- **`report/backlog.json`** expandido: ~125 novas tasks de enrichment (backlog).
- **Decisões de enrichment registradas:** 2FA/TOTP, blacklist, API Keys, activity log,
  FTS, email pluggável, design system CSS, novas views SPA inline.

### 2026-06-10 — MVP completo: 238 épicos done, 437 testes verdes, push main

- **Push para `main`:** commit `96ca46f` (MVP completo — backend FastAPI + frontend + infra + 437 testes).
- **`.github/workflows/`** removido do commit (PAT sem escopo `workflow`).
- **report/backlog.json:** todos os 238 itens done; 4 blocked (dep. externa); revisão cíclica FINAL.
- **Épicos 4ª leva:** BEQ-30 (validado), BEQ-32 (filtro product_id em reviews admin),
  BEQ-33 (buyer_email alias em orders admin), OPS-24 (download metrics no dashboard),
  ADM-12 (AdminAuditReader + X-Total-Count), SEC-20 (CSP via SecurityHeadersMiddleware),
  FE-36 (paginação Próxima/Anterior na home), DOM-37 (domain_event ao expirar cupom),
  ADM-13 (GET /admin/downloads com filtros + X-Total-Count).
- **Ruff limpo:** 34 E501 + 3 F401 corrigidos em testes antigos.
- **Auto-repair:** 0 itens na revisão final.

### 2026-06-10 — Épicos BEQ+DBQ+FE+AUTH+OPS+SEC concluídos (121 testes)

- **STATUS.md** atualizado: 8 épicos fechados; **121 testes** verdes; backlog em 130 itens.
- **BEQ-01..08 (Qualidade Backend):** serviços POO+DI, schemas Pydantic, exception_handlers
  mapeados, `SchemaSync`, `HealthRouter`, seeds externalizados (sem hardcode).
- **DBQ-01..05, 08..10 (Qualidade DB):** constraints CHECK (email/preço), índices de performance
  (slug/email/status), `Decimal` para Money, UML atualizado, `User.deleted_at` LGPD,
  `CreatedAtMixin`/`UpdatedAtMixin` de auditoria.
- **FE-12 (Conta/Perfil fiscal):** `renderAccount()` + rota `#/conta` + botão Conta na nav;
  formulário PF/PJ com `billing_profile` GET/PUT.
- **FE-13 (Filtros por faceta):** chips tag/autor no catálogo; backend aceita `?tag=&?author=`
  com JOIN M2M e `.distinct()` no SQLAlchemy.
- **AUTH-06 (Refresh token):** `JwtService.issue_refresh/verify_refresh`; `POST /auth/refresh`;
  `TokenOut` agora retorna `access_token` + `refresh_token`.
- **OPS-01 (Logging estruturado):** `JsonFormatter` (stdlib), `LoggingConfig.setup()`,
  `CorrelationIdMiddleware` com `ContextVar[str]` para `X-Correlation-ID`.
- **SEC-01 (Rate limiting):** `_InMemoryStore` com sliding window (`deque`); `RateLimit`
  dependency; store em `app.state.rate_store` para isolamento por instância de app/teste.
- **Auto-repair (1):** rate limiter singleton movido de módulo para `app.state` após detectar
  16 falhas de cross-test contamination no `pytest` full-suite.
- **Backlog.json:** revisão cíclica registrada; +5 follow-ups (FE-14, ADM-05, SEC-05, SEC-06, OPS-06). Total: 130 itens.

### 2026-06-10 — Épico Domínios concluído (DOM-01..11)
- **STATUS.md** atualizado: fase = implementação autônoma; backend+storefront no ar em
  Docker com PostgreSQL async (psycopg3); **84 testes** verdes; tabela de estado e lista
  de domínios entregues; corrigido driver (asyncpg → psycopg3) e próximo passo.
- Domínios implementados nesta rodada: **newsletter** (DOM-09), **taxonomia**
  autor/editora/série/tags + facetas (DOM-06), **ativos** ProductFile/ProductImage com
  capas reais no storefront (DOM-07), **perfil fiscal** billing_profile CPF/CNPJ (DOM-10),
  **estorno** refund com revogação de posse anti-pirataria (DOM-11).
- Infra de schema: `SchemaSync` aplica colunas novas no Postgres (`ADD COLUMN IF NOT EXISTS`,
  com aspas em `"order"`) sem perder dados.
- Revisão cíclica do épico: parecer gravado em `report/backlog.json` (`review_summary`),
  grooming do backlog (REV-03) e +3 follow-ups em contexto (DOM-12, FE-12, FE-13). Backlog em 125 itens.

### Adicionado
- `CLAUDE.md`: guia operacional com metodologias obrigatórias (SDD, TDD, PEP 8)
  e regra de trabalho restrito a `.spec/planning/`.
- `STATUS.md`: snapshot inicial — fase de *planning*.
- `CHANGELOG.md`: este arquivo.
- Estrutura `.spec/planning/` para a fase de planejamento.

- `.spec/planning/CHANGELOG.md`: changelog específico da pasta de planning.
- 22 documentos de planning em `.spec/planning/` (Discovery & Produto,
  Arquitetura & Técnico, Qualidade & Processo, Negócio & Operação).

### Alterado
- `STATUS.md`: planning marcado como rascunho completo; decisões de stack
  registradas e pendências consolidadas.
- **Mudança de stack (2026-06-06): Django → FastAPI**; backend e frontend
  **separados** (serviços independentes). Atualizados `CLAUDE.md`, `STATUS.md`
  e todos os 22 documentos de planning afetados (ADR, arquitetura, contratos de
  API, Docker, testes, padrões, roadmap, riscos, etc.). Acréscimos: SQLAlchemy +
  Alembic (ORM/migrations), SQLAdmin (admin), OAuth2+JWT (auth), API JSON com
  OpenAPI automático. Banco PostgreSQL e Mercado Pago mantidos.

- **Fase de unit specs iniciada** em `.spec/unit/`: `README` (catálogo), `_TEMPLATE-unit-spec.md`,
  `CHANGELOG`, índices de área (`backend/`, `db/`, `security/`, `infra/`, `tests/`) e o
  1º exemplo preenchido (`backend/payments/service_process_webhook.md`).
  Granularidade por componente; frontend adiado.
- `CLAUDE.md`/`STATUS.md`: regra de ouro e fase atual atualizadas para `.spec/unit/`
  (planning marcado como concluído/congelado).
- **Padrões de engenharia** em `.spec/standards/` (python-and-tooling, pep8-and-imports,
  solid, oop-and-naming, enforcement): SOLID, POO sem globais, services como classes
  com DI, laços `for` explícitos (sem comprehension/lambda), naming declarativo,
  Python 3.14.5+, enforcement Ruff + pre-commit + revisão.
- `CLAUDE.md` §2.4: passa a exigir leitura de `.spec/standards/` antes de codar.
- `planning/14-padroes-de-codigo.md`: marcado como **superado** pelos standards (histórico).
- `unit/_TEMPLATE-unit-spec.md` e o exemplo `service_process_webhook`: refatorados para
  **service = classe com injeção de dependência** (POO/SOLID).
- **~69 unit specs geradas** em `.spec/unit/` (backend, db, security, infra, tests),
  cada uma com contrato e casos de teste para TDD. Falta o lote da visão completa
  (reviews, cupons, multi-autor, wishlist, RBAC, NF).
- **Trilha de testes** aprofundada: guias `how_to_pytest`, `mocking_guide`,
  `security_testing`, `io_testing` + CHANGELOG próprio + regra de manutenção.
- **Novas trilhas vivas** (cada uma com README + docs + CHANGELOG):
  - `.spec/api/` — contrato da API (OpenAPI como fonte da verdade).
  - `.spec/ops/` — runbooks (deploy, backup/restore, rotação de segredos, exclusão LGPD, incidente).
  - `.spec/observability/` — logging, métricas, alertas, tracing.
  - `.spec/security/` — threat model (STRIDE) em nível de sistema.
- **Lote da visão completa: +31 unit specs** (RBAC, autores/editora/série, tags,
  files/images, reviews, cupons, wishlist, newsletter, cart, entitlement, download_log,
  billing, refund). Total ≈ 100 units. Trilha de testes ajustada para esses domínios.
- **Roadmap vivo** em `.spec/roadmap.md` (sequenciamento por marcos/tiers; substitui
  o do planning/21, congelado).

## 2026-06-10 (manhã) — Autenticação + Painel Admin

### Adicionado
- **AUTH (01–04):** JWT HS256 + hash PBKDF2 (stdlib, leve); model `User` + papéis
  (customer/staff/admin); `POST /api/v1/auth/token` (login), `/register` (comprador),
  `/me`; dependency `get_current_user` + `RequireRole` (RBAC). Admin semeado via env
  (sem hardcode). **Validado ao vivo** (login admin contra Postgres). +13 testes.
- **Admin (SQLAdmin) em `/admin`:** painel CRUD (Produto/Categoria) + leitura
  (Pedido/Pagamento/Usuário/Download), **protegido** por login de staff/admin
  (sessão por cookie). Validado ao vivo (login → 302; sem login → redireciona).
- Infra: túneis no `docker-compose` com `restart: unless-stopped` (recupera pós-reboot).

### Auto-repair (revisão cíclica)
- Pós-reboot do Windows: stack reerguido; túneis movidos para o compose.

## 2026-06-10 (noite) — BE-01/BE-02: backend assíncrono + Postgres

### Alterado
- **Backend migrado para async** (SQLAlchemy `AsyncSession` + `async_sessionmaker` +
  `create_async_engine`): `core/db` (engine async, `get_session` async, lifespan),
  todos os services (`catalog/orders/payments/delivery`) e routers viraram `async`,
  `seeds` e `main` (lifespan) async. `Order.items` com `lazy="selectin"` (async-safe).
- **Banco: PostgreSQL via `asyncpg`** no container (dev/test usam `sqlite+aiosqlite`).
- Testes reescritos para async (`httpx.AsyncClient` + `ASGITransport`, `pytest-asyncio`);
  **22 testes verdes**, Ruff verde.
- `Dockerfile` do backend instala `gcc` só durante o build (asyncpg sem wheel cp314) e o
  remove na mesma camada (imagem enxuta).

## 2026-06-10 — Execução autônoma: backlog, relatório, Docker, qualidade

### Adicionado
- **Backlog mestre** `report/backlog.json` (**121 tarefas**, fragmentadas, com estados)
  — fonte de verdade do progresso; limites 110–250.
- **Página de relatório** `report/app.py` (serviço próprio, lê o backlog, auto-refresh,
  seções A fazer/Em execução/Concluído, barra de progresso).
- **Barra de qualidade** `.spec/quality-bar.md` (backend POO sem amarras, DB
  determinístico/observável, frontend UX correta — centralização certa, tooltips, sem reload).
- **Revisão cíclica** `.spec/self_reflection/cyclic-review.md` (após cada task:
  valida competência → auto-repair → incremento inteligente do backlog; anti-scope).
- **Docker de tudo**: `docker-compose.yml` (db Postgres + backend + report),
  `backend/Dockerfile`, `report/Dockerfile`, `requirements.txt` pinados.
- Regras: **🚫 sem dados em hardcode** e **não sair do contexto** (CLAUDE §2.4/2.5).

### Em execução
- Subir tudo em Docker + **2 túneis Cloudflare** (links separados: app e relatório),
  depois executar o backlog em ordem pela revisão cíclica.

## 2026-06-07 — Decisões fechadas + novos requisitos

### Decidido (propagado para specs/STATUS)
- Versões fixadas (validadas em 3.14.5): FastAPI 0.136.3, SQLAlchemy 2.0.50,
  Pydantic 2.13.4, Uvicorn 0.49.0, etc. (tabela em `standards/python-and-tooling`).
- **Auth: JWT.** **Admin: SQLAdmin na própria API.** **Banco: PostgreSQL async (`asyncpg`)**
  → services `async`. **Deps: uv.** **MVP sem multi-vendedor e sem e-mail transacional.**
  **CI: GitHub Actions, cobertura ≥ 95%.** **Frontend: Next.js.** Download: 5 / 7 dias.

### Novos requisitos (a especificar/implementar)
- **Cadastro dinâmico de e-book** via frontend: por **JSON**, por **link/URL** ou **manual**.
- **Homepage/landing** e **login do comprador** (conta opcional para comprar/navegar melhor).
- **Fluxogramas obrigatórios** (desenvolvimento, backend, frontend, navegação cliente/admin).
- **Docker** no planejamento (compose com Postgres async).
- Checklist mestre do projeto (`.spec/checklist.md`).

### Adicionado
- `standards/docstrings-and-language.md`: código em inglês; docstrings/comentários
  em pt-BR (obrigatório); docstring em TODA funcionalidade; UTF-8.
- `standards/oop-and-naming.md`: regras estruturais (sem `def`-in-`def`, sem arquivo
  só com funções → usar classe/`__call__`, sem classe aninhada); exceção mínima FastAPI.
- `standards/CHANGELOG.md` (a trilha agora tem changelog próprio).
- `unit/infra/ports.md`: **portas não-padrão** (base 48xxx), configuráveis por env.
- Trilha **`.spec/dashboard/`** (evolução do projeto: métricas/gráficos, fontes, cadência).
- Trilha **`.spec/distribution/`** (Cloudflare Tunnel; PC como servidor; PC/celular; alternativas).
- `unit/db/uml-class-diagram.md`: **UML de classe viva**, atualizada a cada migração.

### Alterado
- `unit/security/rbac_authorization` (require_role → classe chamável `RequireRole`) e
  `unit/backend/payments/service_map_status` (função → classe `StatusMapper`) para
  cumprir as novas regras estruturais.
- `CLAUDE.md` §2.4 e tabela de docs; `unit/infra/{env_config,docker_compose,server}` (portas).

### Adicionado (frontend + self_reflection)
- Trilha **`.spec/frontend/`**: dois frontends — **storefront (Next.js/React SSR + TS)**
  e **dashboard-ui** (mesma stack + Recharts/Chart.js); `adr-stack`, `storefront`,
  `dashboard-ui`, `conventions`, `CHANGELOG`.
- Trilha **`.spec/self_reflection/`**: prática de auto-revisão do código pelo agente
  (`process`, `log`, `CHANGELOG`). Esclarecido que `self_reflection` não é frontend.

### Modo autônomo (a partir de 2026-06-07, noite)
- Micael autorizou execução autônoma (sem custos, sem contas): seguir para a **criação
  de código** do MVP, testar e publicar via PC (Cloudflare quick tunnel). Ver progresso
  abaixo e em `.spec/self_reflection/log.md`.

### Adicionado — código do MVP (backend) + deploy
- **`backend/`**: aplicação **FastAPI** (Python 3.14, SQLAlchemy 2, SQLite) implementando
  o MVP: catálogo, pedido (preço congelado), pagamento **simulado** (gateway fake, sem
  conta), **webhook idempotente**, **download seguro** (token/expiração/limite),
  vitrine demo server-rendered + simulador, seeds idempotentes.
- Padrões honrados: services como classes com DI, docstrings pt-BR, sem comprehension/lambda,
  `StrEnum`, imports organizados. **Ruff verde.**
- **Testes:** 22 testes pytest (catálogo, pedidos, webhook/idempotência, download
  válido/expirado/limite, segurança/path-traversal/estados) — todos passando.
- **No ar:** uvicorn em `:48080` + Cloudflare quick tunnel (URL temporária, sem conta).
  Fluxo validado ponta a ponta na API e na web. Scripts em `backend/scripts/`.
- `backend/README.md` com instruções de execução; `backend/.gitignore`.

### Corrigido
- `.gitignore`: adicionada exceção para a pasta `.spec/`, que era ignorada
  pelo padrão `*.spec` (regra do PyInstaller).

---

_Início do projeto: 2026-06-06_
