# ROADMAP (vivo) — e_seller

> Roadmap **vivo** do projeto, atualizado conforme avançamos. Substitui, para fins de
> sequenciamento, o [`planning/21-roadmap.md`](planning/21-roadmap.md) (congelado).
> Datas absolutas quando definidas. Última atualização: 2026-06-06.

---

## Onde estamos

**Fase de especificação.** Resumo:

| Trilha | Estado |
|---|---|
| `planning/` | 🟢 congelado (22 docs) |
| `standards/` | 🟢 vivo (6 docs) |
| `unit/` | 🟢 ~100 unit specs (MVP + visão completa) |
| `api/` `ops/` `observability/` `security/` | 🟢 trilhas vivas criadas |
| Frontend | ⚪ tecnologia a decidir |
| Código de produção | ⚪ não iniciado |

Pendências de spec: migrations dos tiers 🟡/🔵 ([`unit/db/README`](unit/db/README.md));
decisão de frontend; estender schemas de catálogo.

---

## Fase 1 — MVP (Tier 🟢) — implementação (código + TDD)

> Só inicia quando o Micael liberar "codar". Cada marco segue SDD→TDD e a
> [Definition of Done](planning/16-definition-of-done.md).

| Marco | Entrega | Units principais |
|---|---|---|
| **M0** Fundação | FastAPI + Docker + Postgres + Alembic + Ruff + CI verde; `/api/v1/healthz` | `core/*`, `infra/*`, `db/alembic_setup` |
| **M1** Domínio + Admin + Auth | models MVP + migration inicial; SQLAdmin; login JWT | `*/model_*`, `db/migration_initial`, `admin/*`, `accounts/*`, `security/jwt*` |
| **M2** Catálogo (API) | `GET /products`, `/products/{slug}`, `/categories` | `catalog/*` |
| **M3** Pedido + Checkout | `POST /orders` + checkout MP (sandbox) | `orders/*`, `payments/service_create_checkout`, `gateway_mercadopago` |
| **M4** Webhook + Estados | webhook idempotente + máquina de estados | `payments/service_process_webhook`, `service_map_status`, `orders/service_state_machine`, `security/webhook_signature` |
| **M5** Entrega segura | grant (expira/limite) + download protegido → **MVP ✅** | `delivery/*`, `security/download_token`, `file_protection` |

Cross-cutting do MVP: logging básico ([`observability/logging`](observability/logging.md)),
backup do Postgres ([`ops/backup-restore`](ops/backup-restore.md)), revisão do
[threat model](security/threat-model.md).

---

## Fase 2 — Tier 🟡 (próximo)

| Marco | Entrega |
|---|---|
| **M6** Biblioteca/Posse | `entitlement` + "Minha Biblioteca" + `download_log` + reemissão de link |
| **M7** Reviews | avaliação de comprador verificado |
| **M8** Cupons | desconto no checkout (idempotente por pedido) |
| **M9** Carrinho | compra multi-item |
| **M10** Catálogo rico | autores, tags, múltiplos arquivos/imagens; busca/filtros (RF-04) |
| **M11** Estornos | `refund` revoga acesso |

Migration: `db/migration_tier_yellow`.

---

## Fase 3 — Tier 🔵 (visão completa)

| Marco | Entrega |
|---|---|
| **M12** RBAC | `role`/`user_role` + `require_role` (migra `is_staff`) |
| **M13** Editora/Série | `publisher`, `series` |
| **M14** Wishlist + Newsletter | lista de desejos + captação (LGPD) |
| **M15** Faturamento/NF | `billing_profile` + integração fiscal |
| **M16** Frontend dedicado | após decisão de tecnologia (ADR-005) |

Migration: `db/migration_tier_blue`. Cross-cutting: métricas/alertas
([`observability/`](observability/)), OpenAPI client p/ frontend ([`api/openapi-workflow`](api/openapi-workflow.md)).

---

## Decisões pendentes que afetam o roadmap

- [ ] Liberar início da codificação (sair da fase só-spec).
- [ ] Versões exatas (FastAPI/SQLAlchemy/Pydantic em Python 3.14).
- [ ] uv vs pip; driver Postgres sync vs async.
- [ ] Tecnologia do frontend; hospedagem de baixo custo.
- [ ] Provedor de NF (Fase 3).

## Manutenção

Atualizar este roadmap ao concluir cada marco (e registrar no [`CHANGELOG.md`](../CHANGELOG.md) raiz e no `STATUS.md`).
