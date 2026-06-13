# STATUS.md — e_seller

> Snapshot do estado atual do projeto. Atualize ao concluir cada marco
> e registre a mudança no [CHANGELOG.md](CHANGELOG.md).

---

## Fase atual

**🚀 Enrichment (branch `enrichment`)** — todos os 4 épicos concluídos.

AAA (blacklist + TOTP + API Keys + activity log), FEV (design system + 10 views),
DBE (pool tuning + FTS SearchService + índices compostos), BEE (email + /me + health + Problem+JSON).

---

## Estado geral

| Área | Estado |
|---|---|
| Planning | 🟢 Concluído (aprovado, congelado) |
| Unit specs | 🟢 ~100 units (MVP + visão completa) |
| Trilhas vivas (api/ops/observability/security) | 🟢 criadas |
| Testes | 🟢 **494 passando** (437 MVP + 14 FEV + 7 DBE + 15 BEE + outros) + Ruff verde |
| Código de produção (MVP) | 🟢 **Backend completo NO AR em Docker** |
| Épico **DOC** (enrich) | 🟢 Concluído — roadmap, planning, backlog (125 tasks) |
| Épico **AAA** (enrichment) | 🟢 Concluído — blacklist, TOTP 2FA, API Keys, activity log |
| Épico **FEV** (Frontend Visual) | 🟢 Concluído — design system, 10 views, SPA /conta, admin panels, 14 testes DOM |
| Épico **DBE** (DB Enrichment) | 🟢 Concluído — pool tuning, SearchService FTS/ILIKE, migration GIN |
| Épico **BEE** (Backend Enrichment) | 🟢 Concluído — email, /me endpoints, health, Problem+JSON |
| Épico **SFX** (Storefront Fix) | 🟢 Concluído — footer, newsletter CSS, admin link auth-guard, cover placeholder, schema fixes |
| Épico **UXR** (UX Redesign) | 🟡 Em andamento — audit feito, pesquisa de mercado em execução |

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
- **Full-text search:** índice GIN funcional `to_tsvector(portuguese, ...)` no PostgreSQL;
  fallback ILIKE no SQLite (testes). `SearchService` detecta dialeto em runtime.
- **Email:** `EmailService` pluggável (SMTP via settings); ativado quando `SMTP_HOST` definido.
  Métodos: send_purchase_confirmation, send_password_reset, send_download_expiring, send_newsletter_welcome.
- **Frontend:** refatoração CSS com design system (tokens, tipografia, escala de espaço 4px).
  Novas views: `/conta` (SPA), `/biblioteca`, `/carrinho`, `/favoritos`.
- **/me endpoints:** router_me.py com GET /me/orders, /me/library, /me/wishlist, /me/cart.
- **Health enrichment:** db_latency_ms + disk_free_mb em /healthz/detail e /health/detail.
- **Problem+JSON (RFC 9457):** exception_handlers retornam type/title/status/detail/instance
  com Content-Type: application/problem+json.

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
- Commits semânticos por épico (sem push, sem Co-Authored-By).
- Revisão cíclica ao final de cada épico.
- Docker Desktop ativo — nenhum serviço derrubado durante a execução.

---

_Última atualização: 2026-06-13 12:04 — 🟡 UXR Fase 4 concluída (UXR-17..19): hero com CTA 'Ver catálogo' + prova social (contagem real de e-books), faixa de confiança (download imediato/pagamento seguro/acesso vitalício). Próximo: Fase 5 (detalhe e footer)._
