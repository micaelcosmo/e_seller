# ROADMAP (vivo) — e_seller

> Roadmap **vivo** do projeto. Substitui o congelado [`planning/21-roadmap.md`](planning/21-roadmap.md).
> Datas absolutas quando definidas. Última atualização: 2026-06-13.

---

## Estado atual

**MVP completo em `main`.** Backend FastAPI + Jinja2 storefront rodando em Docker.
Branch `enrichment` aberta para AAA + Frontend Visual + DB.

| Trilha | Estado |
|---|---|
| `planning/` | 🟢 congelado (22 docs) |
| `standards/` | 🟢 vivo (6 docs) |
| `unit/` | 🟢 ~100 unit specs |
| `api/` `ops/` `observability/` `security/` | 🟢 trilhas vivas |
| Backend MVP | 🟢 **completo** — 13 domínios, 437 testes verdes, Ruff limpo |
| Frontend MVP | 🟢 **funcional** — 8 templates Jinja2, dark theme, responsivo |
| DB MVP | 🟢 **sólido** — 21 modelos, 9+ índices, constraints CHECK |
| **Enrichment** | 🟡 **em andamento** (branch `enrichment`) |

---

## Fase MVP — concluída ✅

Todos os marcos M0–M16 entregues. Destaques:

| Marco | Entrega | Testes |
|---|---|---|
| M0 Fundação | FastAPI + Docker + Postgres + Alembic + Ruff | ✅ |
| M1 Domínio + Admin + Auth | 21 modelos, migration, SQLAdmin, JWT+RBAC | ✅ |
| M2 Catálogo | `/products`, `/categories`, busca, facetas | ✅ |
| M3 Pedido + Checkout | multi-item, gateway simulado | ✅ |
| M4 Webhook + Estados | idempotência, máquina de estados, HMAC | ✅ |
| M5 Entrega segura | grant (TTL+limite), download auditado | ✅ |
| M6 Biblioteca | entitlement, "Minha Biblioteca", download_log | ✅ |
| M7 Reviews | avaliação de comprador verificado | ✅ |
| M8 Cupons | desconto, auto-desativação, domain event | ✅ |
| M9 Carrinho | compra multi-item | ✅ |
| M10 Catálogo rico | autores, tags, arquivos, imagens, busca facetada | ✅ |
| M11 Estornos | refund revoga acesso | ✅ |
| M12 RBAC | RequireRole, UserRole enum, CUSTOMER/STAFF/ADMIN | ✅ |
| M13 Editora/Série | publisher, series, taxonomia completa | ✅ |
| M14 Wishlist + Newsletter | lista de desejos, captação LGPD | ✅ |
| M15 Faturamento | billing_profile, CPF/CNPJ | ✅ |
| M16 Frontend dedicado | Jinja2 SPA inline (MVP; Next.js Tier 2) | ✅ |

---

## Fase Enrichment — em andamento (2026-06-13)

> Motivação: backend sólido, agora fortalecer segurança (AAA), qualidade visual (FE)
> e capacidade de busca (DB). Nada fora do contexto "vender e-books".

### Épico DOC — Documentação e Planning

Atualizar todos os documentos, criar roadmap incisivo e backlog de enrichment.

| Task | Entrega | Motivo |
|---|---|---|
| DOC-01 | STATUS.md + CHANGELOG.md atualizados | Fonte de verdade |
| DOC-02 | .spec/roadmap.md reescrito | Este documento |
| DOC-03 | .spec/enrichment/ (4 planning docs) | Base para TDD |
| DOC-04 | .spec/tests/ YAML adversariais | Precisão, sem alucinação |
| DOC-05 | report/backlog.json (125 tasks) | Rastreabilidade |

### Épico AAA — Authentication, Authorization, Accounting

> **Motivação:** JWT existe, mas faltam: revogação de tokens, 2FA para admin,
> rastreabilidade de ações do usuário e autenticação programática (API Keys).
> Esses são os pilares de "coparticipação JWT + segurança" pedidos pelo usuário.

| Task | Entrega | Prioridade |
|---|---|---|
| AAA-01..03 | UserActivityLog (modelo, service, log em login) | Alta |
| AAA-04..06 | Activity log em compra + download + perfil + endpoint /me/activity | Alta |
| AAA-07 | Testes activity log | Alta |
| AAA-08..12 | Token blacklist (RevokedToken, service, logout, get_current_user) | Alta |
| AAA-13..17 | API Keys (modelo, service, endpoints, dependency) | Média |
| AAA-18..26 | TOTP 2FA (settings, User.totp_secret, service, enroll, verify, login step-2) | Alta |
| AAA-27..28 | Per-user rate limit + ownership checks reforçados | Média |
| AAA-29..30 | Spec YAML + revisão cíclica | — |

### Épico FEV — Frontend Visual Enrichment

> **Motivação:** frontend funcional mas minimalista. Cada view precisa de:
> design system coerente, componentes reutilizáveis, novas views essenciais
> (conta, biblioteca, carrinho, favoritos) e feedback visual (toast, loading, validation).

| Task | Entrega | Impacto |
|---|---|---|
| FEV-01..08 | Design system CSS + componentes base + toast + loading | Alto |
| FEV-09..16 | Overhaul: index, detalhe, pedido, senha, nav, mobile | Alto |
| FEV-17..22 | Novas views: conta, biblioteca, carrinho, favoritos, newsletter | Alto |
| FEV-23..30 | Admin UI enriquecido, errors pages, favicon, meta OG | Médio |
| FEV-31..35 | Acessibilidade, CSS em arquivo estático, validation JS | Médio |
| FEV-36..40 | Testes HTML + spec YAML + revisão cíclica | — |

### Épico DBE — Database Enrichment

> **Motivação:** busca atual é LIKE (case-insensitive). PostgreSQL tem suporte nativo a
> full-text search com ranking e stemming pt-BR via `tsvector`. Índices compostos
> melhoram queries de relatório admin. Sem mudar o schema de forma quebrada.

| Task | Entrega | Impacto |
|---|---|---|
| DBE-01..05 | FTS: tsvector + índice GIN + trigger + SearchService + endpoint | Alto |
| DBE-06..09 | Índices compostos + pool tuning + EXPLAIN audit | Médio |
| DBE-10..11 | Migration Alembic + UML atualizado | — |
| DBE-12..15 | Testes FTS + seed rico + spec YAML + revisão cíclica | — |

### Épico BEE — Backend Enrichment

> **Motivação:** email transacional falta para engajar usuário pós-compra.
> Endpoints `/me/*` unificam dados do usuário autenticado. Health enrichment
> e OpenAPI melhoram observabilidade e DX.

| Task | Entrega | Impacto |
|---|---|---|
| BEE-01..05 | EmailService pluggável + templates + order_paid + reset + expiring | Alto |
| BEE-06..08 | Health enrichment (DB latency, disk) + Problem+JSON + OpenAPI | Médio |
| BEE-09..14 | /me endpoints (orders, library, wishlist, cart, profile) | Alto |
| BEE-15..20 | Testes + spec YAML + revisão cíclica | — |

---

## Fase 3 — Tier 🔵 (visão futura, não iniciada)

| Marco | Entrega | Dependência |
|---|---|---|
| Mercado Pago real | Integração sandbox→prod | Conta MP |
| Frontend Next.js | React/SSR, client gerado de OpenAPI | TypeScript setup |
| 2FA SMS | OTP via Twilio/Z-API | Conta provedor |
| Watermark | PDF por comprador | pypdf2 ou pdfminer |
| Multi-vendedor | marketplace | Decisão produto |
| NF-e | Nota Fiscal Eletrônica | Provedor fiscal |
| Observabilidade avançada | Prometheus + Grafana | Infra staging |
| Testes E2E browser | Playwright | CI configurado |
| CI/CD completo | GitHub Actions 95% gate | PAT com workflow scope |

---

## Regra de ouro

> **Não sair do contexto:** tudo serve a "vender e-books".
> Rejeitar trabalho fora do objetivo.

---

## Manutenção

Atualizar este roadmap ao concluir cada épico e registrar no CHANGELOG.md.
