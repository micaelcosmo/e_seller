# ✅ Checklist Mestre — e_seller

> Documento **vivo**. `[x]` = feito · `[~]` = parcial/spec pronto · `[ ]` = a fazer.
> Atualizar a cada avanço (junto de STATUS/CHANGELOG). Última: 2026-06-07.

---

## 0. Fundamentos & Processo
- [x] Metodologia SDD + TDD + PEP 8 (`CLAUDE.md`)
- [x] Padrões de engenharia (`.spec/standards/`): SOLID, POO, classes+DI, sem comprehension/lambda
- [x] Idioma: código em inglês, docstrings/comentários pt-BR (UTF-8)
- [x] Regras estruturais: sem def-in-def, sem arquivo só com funções, sem classe aninhada
- [x] Roadmap vivo (`.spec/roadmap.md`)
- [x] Fluxogramas obrigatórios (`.spec/flowcharts/`: dev, backend, frontend, nav cliente, nav admin)
- [x] Auto-reflexão do agente (`.spec/self_reflection/`)
- [ ] Migrar gerência de dependências para **uv** (gerar `uv.lock`)
- [ ] pre-commit + scanner de segredos configurados

## 1. Especificação
- [x] Planning (22 docs, congelado)
- [x] ~135 unit specs (MVP + visão completa)
- [x] Trilhas vivas: api, ops, observability, security, dashboard, distribution, frontend, flowcharts
- [x] UML de classe do DB (atualizar a cada migração)
- [x] Decisões fechadas (JWT, SQLAdmin, Postgres async, uv, cobertura 95%, Next.js, sem multi-vendedor/e-mail no MVP)

## 2. Backend — MVP (Tier 🟢)  — **NO AR**
- [x] FastAPI + estrutura por módulos
- [x] Catálogo (listar publicados, busca, detalhe)
- [x] Pedido com preço congelado
- [x] Pagamento **simulado** (gateway fake, sem conta) + checkout
- [x] Webhook **idempotente** + máquina de estados
- [x] Entrega segura (token, expiração, limite, anti path-traversal)
- [x] Vitrine demo server-rendered + simulador
- [x] Seeds idempotentes
- [x] 22 testes pytest verdes + Ruff verde
- [x] No ar: uvicorn :48080 + Cloudflare quick tunnel

## 3. Backend — migração de stack (débitos do MVP)
- [ ] **SQLite → PostgreSQL** com driver **async (asyncpg)** → services `async`
- [ ] **Alembic** (migrations) no lugar de `create_all`
- [ ] Fixar versões no `pyproject` + `uv.lock`
- [ ] Reavaliar specs que citam sync após migração

## 4. Autenticação & Admin
- [ ] **JWT** (emitir/validar, hash de senha)
- [ ] **Login do comprador** (conta opcional) + `POST /auth/register`
- [ ] **Login admin** + `require_role` (RBAC)
- [ ] **SQLAdmin** montado na API (CRUD de produtos/pedidos)

## 5. Cadastro dinâmico de e-book (novo requisito)
- [~] Spec `ProductRegistrar` (3 modos) pronta
- [ ] Modo **JSON** (colar JSON → validar → rascunho)
- [ ] Modo **Link/URL** (importar manifest; proteção SSRF)
- [ ] Modo **Manual** (formulário)
- [ ] Upload de arquivo do e-book + capa; publicar/despublicar
- [ ] Endpoint admin protegido (`router_admin_products`)

## 6. Frontend — storefront (Next.js, inspiração **Sellfy**)
- [~] Specs (stack, páginas, convenções, referências de design)
- [ ] **Home / landing** (destaques + CTA)
- [ ] Catálogo + busca + filtros
- [ ] Página do e-book (SSR/SEO)
- [ ] **Login/cadastro do comprador**; conta + histórico
- [ ] Checkout + acompanhamento do pedido
- [ ] **Minha Biblioteca** (posses) + wishlist
- [ ] Área admin: cadastro dinâmico (JSON/link/manual)
- [ ] Design system mínimo (Tailwind?) estilo Sellfy

## 7. Frontend — dashboard-ui (self-observação)
- [~] Spec `dashboard-ui`
- [ ] Gerar `dashboard.json` a partir dos artefatos
- [ ] Gráficos (objetivos, progresso, marcos, decisões, riscos)

## 8. Domínios da visão completa (Tiers 🟡/🔵)
- [~] Specs prontas (units)
- [ ] Entitlement + "Minha Biblioteca" + download_log
- [ ] Reviews (comprador verificado)
- [ ] Cupons (desconto no checkout)
- [ ] Carrinho (multi-item)
- [ ] Autores/editora/série, tags, múltiplos arquivos/imagens
- [ ] RBAC completo · Wishlist · Newsletter · Billing/NF · Refund

## 9. Infra / CI / Deploy
- [~] Specs Docker (compose com Postgres async) — `unit/infra/docker_compose`
- [ ] Dockerfile backend + frontend + `docker-compose.yml` reais
- [ ] **CI: GitHub Actions** (Ruff + pytest + cobertura **≥ 95%**)
- [ ] Portas não-padrão 48xxx aplicadas no compose
- [ ] Distribuição: **túnel nomeado** (URL estável) — precisa conta Cloudflare grátis
- [ ] Backup do Postgres (runbook `ops/backup-restore`)

## 10. Pagamentos (real)
- [ ] Integração **Mercado Pago real** (Pix/cartão/boleto) — precisa conta
- [ ] Validação de assinatura do webhook (RNF-02)

## 11. Observabilidade & Operação
- [~] Specs (logging, métricas, alertas, runbooks)
- [ ] Logging estruturado + correlation id
- [ ] Métricas + alertas (webhook, downloads, latência)
- [ ] Runbooks validados (deploy, backup, LGPD, incidente)

## 12. Segurança & LGPD
- [x] Token seguro, storage protegido, idempotência (no MVP)
- [~] Threat model (STRIDE)
- [ ] LGPD: exclusão de dados (procedimento + endpoint)
- [ ] Rate limiting (login/webhook/download)
- [ ] Política de privacidade/termos

---

### Legenda de prioridade sugerida (próximos passos)
1. Frontend Next.js (home, catálogo, produto, checkout) — inspiração Sellfy.
2. Auth (JWT) + login do comprador + admin.
3. Cadastro dinâmico de e-book (JSON/link/manual).
4. Migrar para Postgres async + Alembic + uv + CI.
