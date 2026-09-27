# STATUS.md — e_seller

> Snapshot do estado atual do projeto. Atualize ao concluir cada marco
> e registre a mudança no [CHANGELOG.md](CHANGELOG.md).

---

## Fase atual

**🧪 Enrichment + QA (branch `enrichment`)** — `/qa` adotado, épico **QAF** (ajustes que o QA
provou) e épico **VIS** (tapa visual Material 3) concluídos em 2026-09-27. **5 decisões bloqueantes**
aguardando o dono em [`.spec/decisoes-pendentes.md`](.spec/decisoes-pendentes.md).

AAA (blacklist + TOTP + API Keys + activity log), FEV (design system + 10 views),
DBE (pool tuning + FTS SearchService + índices compostos), BEE (email + /me + health + Problem+JSON).

---

## Estado geral

| Área | Estado |
|---|---|
| Planning | 🟢 Concluído (aprovado, congelado) |
| Unit specs | 🟢 ~100 units (MVP + visão completa) |
| Trilhas vivas (api/ops/observability/security) | 🟢 criadas |
| Testes | 🟢 **525 passando** (pytest, SQLite) + Ruff verde · `/qa` no Postgres real: 54/54 pontos de integração e 20/20 jornadas válidos (2026-09-27) |
| Código de produção (MVP) | 🟢 **Backend completo NO AR em Docker** |
| Épico **DOC** (enrich) | 🟢 Concluído — roadmap, planning, backlog (125 tasks) |
| Épico **AAA** (enrichment) | 🟢 Concluído — blacklist, TOTP 2FA, API Keys, activity log |
| Épico **FEV** (Frontend Visual) | 🟢 Concluído — design system, 10 views, SPA /conta, admin panels, 14 testes DOM |
| Épico **DBE** (DB Enrichment) | 🟢 Concluído — pool tuning, SearchService FTS/ILIKE, migration GIN |
| Épico **BEE** (Backend Enrichment) | 🟢 Concluído — email, /me endpoints, health, Problem+JSON |
| Épico **SFX** (Storefront Fix) | 🟢 Concluído — footer, newsletter CSS, admin link auth-guard, cover placeholder, schema fixes |
| Épico **UXR** (UX Redesign) | 🟢 Concluído — design system, header, cards (rating/badges), hero, footer, estados vazios; backend enriquecido (avg_rating/featured/filtro preço) |
| **QA (skill `/qa`)** | 🟢 Adotado — stack isolada `eseller-qa` (48273/48280/48532), 22 histórias, 54 pontos de integração, 20 jornadas, base visual de 4 perfis; relatórios em [`qa-harness/relatorios/`](qa-harness/relatorios/) |
| Épico **QAF** (ajustes do QA) | 🟢 18 achados corrigidos com teste ([`roadmap-qaf.md`](.spec/enrichment/roadmap-qaf.md)) · 🔴 5 bloqueados por decisão do dono |
| Épico **VIS** (Material 3) | 🟢 Storefront e páginas do backend na mesma linguagem, paleta preservada, responsivo ([`roadmap-vis.md`](.spec/frontend/roadmap-vis.md)) |

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

- [ ] ⚠️ **Decisões bloqueantes do QA** ([`.spec/decisoes-pendentes.md`](.spec/decisoes-pendentes.md)):
  D18 painéis HTML de admin inacessíveis no navegador · D19 limite de login/HTTPS atrás do nginx ·
  D20 banco padrão do compose de dev (`e_seller2` × `e_seller`) · D21 política de privacidade diz
  Argon2 (sistema usa PBKDF2) · D22 gateway Mercado Pago real inexistente.
- [ ] Conta Mercado Pago real (credenciais — bloqueado externamente; ver D22).
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

## 🌙 Execução autônoma (QA + QAF + VIS, 2026-09-27 03:40–06:49)

- **Proteções:** Claude não roda comandos de versionamento nem lê `.env` (deny + hook, CLAUDE.md §2.6).
- **`/qa` estabilizado** na stack isolada `eseller-qa` (portas livres 48273/48280/48532; credenciais
  aleatórias fora do git; evidência de API com segredos mascarados — varredura: 0 vazamentos).
- **Rodadas:** 1 → 53 válidos/16 falhas/9 inválidas · 2 → 75/3/0 · 3 → 78/1/0 · 4 → 78/1/0.
  A falha restante é a base visual do admin: painéis HTML da decisão bloqueante **D18**.
- **Responsividade:** loja sem rolagem horizontal em notebook (1366px) e celular (390px), todos os perfis.
- **Relatórios:** [`qa-harness/relatorios/`](qa-harness/relatorios/) (rodada final `2026-09-27-0610`).
- **Nada commitado** — proposta de commits em blocos entregue ao dono.

---

_Última atualização: 2026-09-27 06:49 — 🧪 `/qa` adotado e estável; QAF (18 achados corrigidos com teste, 5 bloqueados por decisão do dono) e VIS (Material 3) concluídos; 525 testes + Ruff verdes; rodada final do `/qa` com 78 válidos e 1 falha (D18)._
