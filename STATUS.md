# STATUS.md — e_seller

> Snapshot do estado atual do projeto. Atualize ao concluir cada marco
> e registre a mudança no [CHANGELOG.md](CHANGELOG.md).

---

## Fase atual

**⚙️ Implementação autônoma** — backend FastAPI + storefront SPA rodando em Docker,
guiados pelo [`report/backlog.json`](report/backlog.json) com revisão cíclica por épico.

O planning e as unit specs estão concluídos; agora executamos o backlog (spec → TDD → código → verificação ao vivo).

---

## Estado geral

| Área | Estado |
|---|---|
| Planning | 🟢 Concluído (aprovado, congelado) |
| Unit specs | 🟢 ~100 units (MVP + visão completa) |
| Trilhas vivas (api/ops/observability/security) | 🟢 criadas |
| Testes | 🟢 **121 passando** (pytest async) + Ruff verde |
| Código de produção | 🟢 **Backend + storefront NO AR em Docker** (FastAPI + PostgreSQL async) |
| Épico **Domínios** (DOM-01..11) | 🟢 **Concluído** e validado ao vivo |
| Épico **Qualidade Backend** (BEQ-01..08) | 🟢 **Concluído** — serviços POO+DI, schemas, exception_handlers, SchemaSync, health, seeds |
| Épico **Qualidade DB** (DBQ-01..05, 08..10) | 🟢 **Concluído** — constraints CHECK, índices, Decimal Money, UML, LGPD, auditoria |
| Épico **Frontend** (FE-12, FE-13) | 🟢 **Concluído** — conta/perfil fiscal, filtros por faceta chips |
| Épico **Auth** (AUTH-06) | 🟢 **Concluído** — refresh token (issue/verify/endpoint) |
| Épico **Ops/Observability** (OPS-01) | 🟢 **Concluído** — logging JSON estruturado + CorrelationId middleware |
| Épico **Segurança** (SEC-01) | 🟢 **Concluído** — rate limiting sliding window in-memory |

**Domínios entregues:** catálogo + busca, cadastro dinâmico (manual/JSON/link), contas+JWT+RBAC,
admin SQLAdmin, compra multi-item, pagamento simulado (gateway fake), webhook idempotente,
download seguro auditado, entitlement/Biblioteca, cupons, reviews de comprador, carrinho, wishlist,
newsletter, **taxonomia** (autor/editora/série/tags + facetas), **ativos** (ProductFile/ProductImage,
capas reais), **perfil fiscal** (billing_profile, CPF/CNPJ) e **estorno** (refund com revogação de posse).

Legenda: ⚪ Não iniciado · 🟡 Em andamento · 🟢 Concluído · 🔴 Bloqueado

- 22 documentos de planning em [`.spec/planning/`](.spec/planning/) (4 grupos).
- 6 docs de padrões em [`.spec/standards/`](.spec/standards/).
- ~69 unit specs em [`.spec/unit/`](.spec/unit/) (backend, db, security, infra, tests;
  frontend adiado); granularidade por componente, services = classe+DI.
- Trilha de testes aprofundada ([`.spec/unit/tests/`](.spec/unit/tests/): guias de pytest, mock, segurança, I/O).
- Novas trilhas vivas: [`.spec/api/`](.spec/api/), [`.spec/ops/`](.spec/ops/),
  [`.spec/observability/`](.spec/observability/), [`.spec/security/`](.spec/security/) (threat model).
- **Visão completa gerada** (+31 units): RBAC, autores/editora/série, tags, files/images,
  reviews, cupons, wishlist, newsletter, cart, entitlement, download_log, billing, refund. **Total ≈ 100 units.**
- Trilha de testes ajustada para os novos domínios.
- **Roadmap vivo** em [`.spec/roadmap.md`](.spec/roadmap.md) (substitui o sequenciamento do planning/21 congelado).
- **Padrões reforçados (2026-06-07):** código em inglês + docstrings/comentários pt-BR (obrigatório),
  docstring em toda funcionalidade, sem `def`-in-`def`, sem arquivo só com funções, sem classe aninhada.
- **Portas não-padrão** (base 48xxx) — [`.spec/unit/infra/ports.md`](.spec/unit/infra/ports.md).
- Novas trilhas: [`.spec/dashboard/`](.spec/dashboard/) (evolução do projeto) e
  [`.spec/distribution/`](.spec/distribution/) (Cloudflare Tunnel, PC-as-server).
- **UML de classe do DB** ([`.spec/unit/db/uml-class-diagram.md`](.spec/unit/db/uml-class-diagram.md)), viva (atualizar a cada migração).
- Frontend (storefront) + `self_reflection`: a definir (stack em discussão).

---

## Decisões já tomadas

- Metodologia: Spec-Driven Development + Test-Driven Development + PEP 8.
- **Padrões de engenharia** ([`.spec/standards/`](.spec/standards/)): SOLID, POO (sem globais,
  `self.` no `__init__`), services = classes com DI, laços explícitos (sem comprehension/lambda),
  naming declarativo; enforcement Ruff + pre-commit + revisão.
- **Backend:** **FastAPI** + Python 3.14.5+ (API JSON; Uvicorn/Gunicorn).
- **ORM/migrations:** SQLAlchemy 2.x + Alembic.
- **Banco:** **PostgreSQL** com driver **async `psycopg3`** (`postgresql+psycopg://`) → services `async`.
  (asyncpg não tem wheel para cp314; SQLite+aiosqlite nos testes.)
- **Admin:** **SQLAdmin** montado na própria API FastAPI (não no frontend).
- **Auth:** **JWT**.
- **Pagamentos:** Mercado Pago (Pix/cartão/boleto).
- **Infra:** Docker em todos os serviços; **backend e frontend separados**.
- **Gerência de dependências:** **uv** (lockfile `uv.lock`).
- **Versões fixadas** (validadas em 3.14.5): FastAPI 0.136.3, SQLAlchemy 2.0.50,
  Pydantic 2.13.4, Uvicorn 0.49.0 — tabela em [`.spec/standards/python-and-tooling.md`](.spec/standards/python-and-tooling.md).
- **MVP:** **sem** multi-vendedor; **sem** e-mail transacional.
- **CI:** GitHub Actions, **gate de cobertura 95%**.
- **Deploy de baixo custo:** PC como servidor + Cloudflare Tunnel (por ora).
- **Download:** `max_downloads = 5`, expiração `7 dias` (padrão).
- **Custo inicial:** zero (ferramentas open-source/gratuitas).
- **Frontend:** **Next.js** (React/SSR), serviço separado, consome a API.

---

## Pendências / Decisões abertas

> A maioria foi **fechada em 2026-06-07** (ver "Decisões já tomadas"). Restam:

- [ ] Validar a versão exata de `asyncpg` em runtime (Python 3.14.5).
- [ ] Conta Cloudflare p/ **túnel nomeado** (URL estável) — opcional.
- [ ] Conta Mercado Pago p/ integração **real** (hoje gateway fake).
- [ ] Hospedagem definitiva de baixo custo (além do PC) — futuro.
- [ ] Detalhar migrations Alembic dos tiers 🟡/🔵.
- [ ] **Cadastro dinâmico de e-book** (JSON / link / manual) — novo requisito a implementar.

---

## 🤖 Execução autônoma (2026-06-10)

- **Backlog mestre** (130 tarefas) em [`report/backlog.json`](report/backlog.json) — fonte de verdade.
- **Página de relatório** (`report/`) + **Docker** (`docker-compose.yml`: db Postgres + backend + report).
- **Barra de qualidade** ([`.spec/quality-bar.md`](.spec/quality-bar.md)) + **revisão cíclica**
  ([`.spec/self_reflection/cyclic-review.md`](.spec/self_reflection/cyclic-review.md)).
- Regras: sem hardcode, não sair do contexto, backlog entre 110–250.
- **Subindo tudo em Docker** + 2 túneis Cloudflare (app + relatório). Links abaixo quando prontos.

## 🚀 No ar (modo autônomo, 2026-06-07)

- **Backend MVP** em `backend/` (FastAPI + SQLAlchemy + SQLite), seguindo os padrões
  (classes+DI, docstrings pt-BR, sem comprehension/lambda). **22 testes verdes**, Ruff ok.
- **Rodando localmente:** `http://localhost:48080` (API em `/api/v1`, docs em `/docs`, vitrine em `/`).
- **Link público (Cloudflare quick tunnel, sem conta/custo):**
  `https://xbox-contest-globe-settled.trycloudflare.com`
  > ⚠️ URL **temporária** (muda a cada reinício do túnel). Para subir de novo:
  > `powershell -ExecutionPolicy Bypass -File backend\scripts\serve_public.ps1`.
  > O link só responde com o PC ligado e os processos (uvicorn + cloudflared) ativos.
- **Fluxo validado ponta a ponta** (API e web): catálogo → compra → pagamento
  **simulado** (sem conta Mercado Pago) → webhook idempotente → download seguro.

Detalhes de execução: [`backend/README.md`](backend/README.md).

## Próximo passo

1. Épicos BEQ, DBQ, FE, AUTH, OPS-01, SEC-01 **fechados** (revisão cíclica registrada no `report/backlog.json`).
2. Próximos épicos: **CI/CD** (CI-01..04: GitHub Actions, pre-commit, gitleaks, Docker build),
   **Observabilidade restante** (OPS-02..05: métricas, alertas, backup, dashboard.json),
   **Segurança/LGPD** (SEC-02..06: LGPD deletion, CORS restritivo, privacy texts, threat model),
   **Pagamentos reais** (PAY-01..03: Mercado Pago), **Frontend** (FE-14, ADM-05, FE-02, FE-09/10, UX).
3. Integração **real** do Mercado Pago quando houver conta (hoje gateway fake).

---

_Última atualização: 2026-06-10 (épicos BEQ+DBQ+FE+AUTH+OPS-01+SEC-01 concluídos; 121 testes; 130 backlog items)_
