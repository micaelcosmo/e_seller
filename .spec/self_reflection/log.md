# Log de Auto-Reflexão

> Entradas cronológicas. Mais recente no topo. Formato em [`process.md`](process.md).

---

## 2026-06-10 (automode) — Fechamento do épico Domínios (DOM-01..11)

**Fiz:** Conclusão dos domínios restantes com TDD e verificação ao vivo em Docker:
**newsletter** (DOM-09), **taxonomia** autor/editora/série/tags + facetas `GET /authors|/tags`
(DOM-06), **ativos** ProductFile/ProductImage com capas reais no storefront (DOM-07),
**perfil fiscal** billing_profile com CPF/CNPJ validado/normalizado (DOM-10) e **estorno**
refund com **revogação de posse anti-pirataria** (DOM-11). 84 testes verdes, Ruff limpo.
SQLAdmin ganhou views para todas as novas entidades.

**Bom:** Padrões honrados (classes+DI, docstrings pt-BR, laços explícitos, sem hardcode).
Estorno integrado à máquina de estados (PAID→REFUNDED) e remove o e-book da Biblioteca —
validado ao vivo. `SchemaSync` aplica colunas novas no Postgres sem recriar o banco/perder
dados (`ADD COLUMN IF NOT EXISTS`, com aspas em `"order"` por ser palavra reservada).

**Gotcha resolvido:** SQLAlchemy async dispara `MissingGreenlet` ao serializar relações
não carregadas. Solução: anexar taxonomia/ativos e **inicializar coleções (mesmo vazias)
enquanto o produto é transitório**, antes do flush — assim a serialização não faz lazy-load.

**Auto-repair (revisão cíclica):** 0 falhas de aceite. Incremento: +3 follow-ups em contexto
— **DOM-12** (invalidar DownloadGrants ativos no estorno: posse é revogada, mas tokens já
emitidos seguem válidos até expirar — gap anti-pirataria real), **FE-12** (página de conta/perfil
fiscal), **FE-13** (filtro por tag/autor usando as facetas). Backlog em 125 itens (110–250 ok).

**A melhorar / dívidas:** DOM-12 acima; testes usam aiosqlite (caminho Postgres do SchemaSync
validado manualmente, não em CI); frontend ainda é SPA leve (Next.js segue como evolução).

**Próximo:** próximo épico (Qualidade backend/DB, CI/CD, observabilidade ou os follow-ups FE).

---

## 2026-06-10 (noite, automode) — Backend async + Postgres + Alembic + relatório

**Fiz:** Página de relatório (Docker, link próprio, relógio Brasília + parecer). Migração
do backend para **async** (AsyncSession; services/routers/seeds/main; `lazy="selectin"`).
Banco **PostgreSQL** em Docker. **Alembic** (env síncrono) + migration inicial autogerada
e validada. 22 testes async verdes, Ruff verde. Tudo no ar em Docker, 2 túneis.

**Bom:** Fluxo de valor validado contra Postgres (compra→pago→download, idempotente).
Padrões mantidos (classes+DI, docstrings pt-BR, sem comprehension/lambda).

**Auto-repair (revisão cíclica):**
- **asyncpg → psycopg3**: asyncpg não tem wheel cp314 (exigia gcc/compilar). psycopg3
  tem wheel binário, é mais leve e suporta sync (Alembic) + async (app). Specs ajustadas.

**A melhorar / dívidas:** Alembic ainda não está no entrypoint do container (app usa
`create_all` em dev) — fica para INFRA-06. `uv` adiado (pip+pin funcionando). Tests usam
aiosqlite (rápido), Postgres validado manualmente.

**Próximo:** AUTH-01 (JWT + hash de senha), depois contas/admin e cadastro dinâmico.

---

## 2026-06-07 (noite) — Implementação do MVP + deploy (autônomo)

**Fiz:** Backend FastAPI (SQLite) com catálogo, pedido (preço congelado), pagamento
simulado (gateway fake, sem conta), webhook idempotente, download seguro
(token/expiração/limite), vitrine demo + simulador, seeds. 22 testes pytest verdes,
Ruff verde. No ar via uvicorn :48080 + Cloudflare quick tunnel. Trilhas frontend e
self_reflection criadas; padrões reforçados (idioma/docstrings/estrutura); portas
48xxx; UML de classe do DB; trilhas api/ops/observability/security/dashboard/distribution.

**Bom:**
- Fluxo de valor ponta a ponta funcionando e testado (incl. idempotência e RNF-01).
- Padrões honrados no código (classes+DI, docstrings pt-BR, sem comprehension/lambda, StrEnum).
- Pagamento simulado permite demonstrar TUDO sem conta/custo.

**A melhorar / dívidas (honesto):**
- Banco do MVP usa `create_all` + **SQLite**, não Alembic/Postgres (specs cobrem; é débito de implementação).
- **Auth/JWT, SQLAdmin, RBAC, entitlement/biblioteca, cupons, refund** ainda não codados (só specs).
- **Frontend Next.js** não codado: há uma **vitrine demo embutida** (server-rendered) para o "no ar".
- Túnel `trycloudflare` é **efêmero** (URL muda; cai se o PC desligar) — webhook real exigirá túnel nomeado.
- Mercado Pago real não integrado (sem conta) — gateway fake no lugar.
- Specs da visão completa não 100% reconferidas após regras estruturais (corrigi os casos óbvios).

**Suposições assumidas:** SQLite + gateway fake + quick tunnel para cumprir "sem custo/sem conta";
escopo de código = MVP; portas 48xxx.

**Ações (próximos passos):** Next.js storefront; Alembic+Postgres; auth/admin; integrar MP quando houver conta;
gerar `dashboard.json`; túnel nomeado para URL estável.

---

## 2026-06-07 — Fase de especificação (planning → unit → trilhas) + início do código

**Fiz:** Planning (22 docs), standards (regras de POO/SOLID/idioma/estrutura), ~104 unit
specs (MVP + visão completa), trilhas vivas (api, ops, observability, security, dashboard,
distribution, frontend), roadmap vivo, UML do DB, portas não-padrão.

**Bom:**
- Desenho de DB com `entitlement` (posse) separado de `download_grant` (link), resolvendo posse única.
- Padrões fortes e enforcement definido; tensão FastAPI×regras resolvida com classe chamável.
- Trilhas vivas com CHANGELOG próprio; rastreabilidade RF/RNF/US.

**A melhorar / dívidas:**
- ~104 unit specs foram escritas; nem todas foram re-verificadas 1-a-1 após as regras
  estruturais novas (só corrigi `RequireRole` e `StatusMapper`). Outros docs podem citar
  funções soltas — ajustar ao implementar.
- Migrations dos tiers 🟡/🔵 ainda não detalhadas.
- Frontend Next.js ainda não scaffoldado em código.

**Suposições assumidas (modo autônomo, Micael dormindo):**
- Sem custo e sem criar contas → Postgres via Docker se disponível; senão **SQLite** local
  para o app rodar sem setup. Distribuição via **Cloudflare quick tunnel** (`trycloudflare`, sem conta).
- Escopo de código nesta rodada = **MVP (Tier 🟢)**: catálogo → pedido → webhook → entrega,
  com testes. Visão completa fica como spec.
- Portas 48xxx conforme combinado.

**Ações:**
- Implementar backend MVP com TDD e deixar testes verdes.
- Subir local (uvicorn :48080) + túnel público.
- Registrar tudo em STATUS/CHANGELOG/dashboard ao final.
