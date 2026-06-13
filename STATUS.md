# STATUS.md — e_seller

> Snapshot do estado atual do projeto. Atualize ao concluir cada marco
> e registre a mudança no [CHANGELOG.md](CHANGELOG.md).

---

## Fase atual

**🚀 Enrichment (branch `enrichment`)** — AAA (Authentication/Authorization/Accounting),
refatoração visual completa do frontend e enriquecimento do banco de dados.

Backend MVP está completo (238 tarefas done, 437 testes verdes, Ruff limpo, branch `main`).
Agora expandimos segurança, UX e qualidade de dados.

---

## Estado geral

| Área | Estado |
|---|---|
| Planning | 🟢 Concluído (aprovado, congelado) |
| Unit specs | 🟢 ~100 units (MVP + visão completa) |
| Trilhas vivas (api/ops/observability/security) | 🟢 criadas |
| Testes | 🟢 **437 passando** (pytest async) + Ruff verde |
| Código de produção (MVP) | 🟢 **Backend completo NO AR em Docker** |
| Épico **DOC** (enrich) | 🟡 Em andamento — roadmap, planning, backlog |
| Épico **AAA** (enrichment) | ⚪ Aguardando |
| Épico **FEV** (Frontend Visual) | ⚪ Aguardando |
| Épico **DBE** (DB Enrichment) | ⚪ Aguardando |
| Épico **BEE** (Backend Enrichment) | ⚪ Aguardando |

**Domínios entregues (main):** catálogo + busca, cadastro dinâmico, contas+JWT+RBAC,
admin SQLAdmin, compra multi-item, pagamento simulado, webhook idempotente,
download seguro auditado, entitlement/Biblioteca, cupons, reviews, carrinho, wishlist,
newsletter, taxonomia, ativos (ProductFile/ProductImage), perfil fiscal, estorno,
paginação, domain events, admin downloads dashboard, rate limiting, logging estruturado.

Legenda: ⚪ Não iniciado · 🟡 Em andamento · 🟢 Concluído · 🔴 Bloqueado

---

## Specs de enrichment

| Documento | Propósito |
|---|---|
| [`.spec/enrichment/roadmap-aaa.md`](.spec/enrichment/roadmap-aaa.md) | Detalhes AAA: TOTP, API Keys, blacklist, activity log |
| [`.spec/enrichment/roadmap-frontend.md`](.spec/enrichment/roadmap-frontend.md) | Frontend visual: design system, views |
| [`.spec/enrichment/roadmap-db.md`](.spec/enrichment/roadmap-db.md) | DB: FTS, índices compostos, pool |
| [`.spec/enrichment/roadmap-backend.md`](.spec/enrichment/roadmap-backend.md) | Backend: email, /me, health, OpenAPI |
| [`.spec/tests/`](.spec/tests/) | Specs de teste YAML por tópico (adversarial) |

---

## Decisões já tomadas (MVP, mantidas)

- Metodologia: SDD + TDD + PEP 8 + revisão cíclica por épico.
- **Backend:** FastAPI + Python 3.14.5+ (API JSON; Uvicorn/Gunicorn).
- **ORM/migrations:** SQLAlchemy 2.x + Alembic.
- **Banco:** PostgreSQL async (psycopg3); aiosqlite nos testes.
- **Admin:** SQLAdmin montado na API FastAPI.
- **Auth:** JWT HS256 (stdlib) + PBKDF2-HMAC-SHA256.
- **Pagamentos:** Mercado Pago (sandbox hoje, real quando conta ativa).
- **Infra:** Docker; backend e frontend separados.
- **Gerência de deps:** uv (lockfile `uv.lock`).
- **Versões fixadas:** FastAPI 0.136.3, SQLAlchemy 2.0.50, Pydantic 2.13.4.
- **Frontend MVP:** Jinja2 + vanilla JS (storefront SPA inline).
- **CI:** GitHub Actions, gate cobertura 95% (pendente).
- **Deploy:** PC + Cloudflare Tunnel (custo zero).

## Novas decisões (Enrichment 2026-06-13)

- **2FA/TOTP:** `pyotp` + `qrcode`; enforcement para staff/admin.
- **Token blacklist:** tabela `RevokedToken` com TTL; verificada em `get_current_user`.
- **API Keys:** hash SHA-256; autenticação alternativa ao JWT para integrações.
- **Activity Log:** `UserActivityLog` model; registra login, compra, download, perfil.
- **Full-text search:** índice `tsvector` GIN no PostgreSQL (products).
- **Email:** `EmailService` pluggável (SMTP via settings); ativado quando `SMTP_HOST` definido.
- **Frontend:** refatoração CSS com design system (tokens, tipografia, escala de espaço).
- **Novas views:** `/conta`, `/biblioteca`, `/carrinho`, `/favoritos` (SPA inline Jinja2).

---

## Pendências / Decisões abertas

- [ ] Conta Mercado Pago real (credenciais — bloqueado externamente).
- [ ] Frontend Next.js (Tier 2 — adiado; MVP usa Jinja2).
- [ ] CI/CD GitHub Actions (PAT sem escopo `workflow` — pendente).
- [ ] Hospedagem definitiva (além do PC) — futuro.

---

## 🤖 Execução autônoma (Enrichment, 2026-06-13)

- **Branch:** `enrichment` (criada de `main` em 2026-06-13).
- **Backlog mestre** em [`report/backlog.json`](report/backlog.json) — ~125 novas tasks (DOC+AAA+FEV+DBE+BEE).
- Commits semânticos por task (sem push, sem Co-Authored-By).
- Revisão cíclica ao final de cada épico.
- Docker Desktop ativo — nenhum serviço derrubado durante a execução.

---

## Próximos passos (ordem de execução)

1. **DOC** — atualizar todos os documentos + roadmap + backlog ← *em andamento*
2. **AAA** — TOTP, blacklist, API Keys, activity log
3. **FEV** — design system CSS, todas as views overhauled
4. **DBE** — FTS, índices compostos, pool tuning
5. **BEE** — email service, /me endpoints, health enrichment

---

_Última atualização: 2026-06-13 (branch enrichment criada; 238 done + 437 testes em main; início do enrichment)_
