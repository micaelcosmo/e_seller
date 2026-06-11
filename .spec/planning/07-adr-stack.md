# 07 — ADR: Stack Tecnológica

> Architecture Decision Record · e_seller · 2026-06-06 (revisado p/ FastAPI)
> Status: **Aceito** (decisões base do Micael)

---

## 💡 O que é um ADR?

Um **Architecture Decision Record** registra *uma decisão*, seu *contexto* e suas
*consequências*. Serve para que, meses depois, qualquer pessoa entenda **por que**
algo foi escolhido — e o que mudaria se a decisão fosse revista.

> **Mudança importante (2026-06-06):** a stack de backend passou de Django para
> **FastAPI**, com **backend e frontend separados**. Isso afeta admin, ORM,
> migrations e autenticação — antes "de graça" no Django, agora escolhidos
> explicitamente abaixo.

---

## ADR-001 — Linguagem e framework de backend

- **Contexto:** queremos um backend **API-first**, com backend e frontend
  **separados** (serviços independentes). Performance e contratos claros importam.
- **Decisão:** **FastAPI** em **Python 3.14.5+**, servido por **Uvicorn** (ASGI);
  em produção, Uvicorn workers sob **Gunicorn**.
- **Consequências:**
  - ✅ API-first nativo; **OpenAPI/Swagger automático** em `/docs` → contrato vivo.
  - ✅ Validação de dados com **Pydantic v2** embutida.
  - ✅ Suporte a `async` (útil para chamadas ao Mercado Pago).
  - ⚠️ **Não há admin, ORM nem auth prontos** (ver ADR-002, ADR-007, ADR-008).
  - ✅ Boa compatibilidade esperada com Python 3.14 (risco menor que o Django tinha).

## ADR-002 — ORM e migrations

- **Contexto:** FastAPI não inclui ORM. Precisamos de persistência relacional e migrations versionadas.
- **Decisão:** **SQLAlchemy 2.x** (ORM) + **Alembic** (migrations).
- **Consequências:**
  - ✅ Padrão de mercado, gratuito, maduro.
  - ✅ Alembic versiona o schema (equivalente às migrations do Django).
  - ⚠️ Mais código de configuração inicial (engine, session, base) do que no Django.

## ADR-003 — Banco de dados

- **Decisão:** **PostgreSQL** (em container), driver `psycopg` (v3).
- **Consequências:**
  - ✅ Robusto, gratuito, ótimo com SQLAlchemy. Reproduzível via Docker. Custo zero.
  - ❌ SQLite descartado para produção; pode servir só para testes rápidos locais.

## ADR-004 — Pagamentos

- **Decisão:** **Mercado Pago** via API oficial + **webhooks** para confirmação.
- **Consequências:**
  - ✅ Cobre Pix/cartão/boleto; sandbox gratuito.
  - ⚠️ Exige endpoint de webhook idempotente e validação de autenticidade.

## ADR-005 — Arquitetura de frontend (separado)

- **Contexto:** Micael decidiu **backend e frontend separados**; tecnologia de
  frontend adiada.
- **Decisão:** Backend é uma **API JSON pura**; o frontend será um **serviço
  independente** (container/repo próprio) consumindo a API. Tecnologia a definir.
- **Consequências:**
  - ✅ Desacoplamento total; o frontend pode ser trocado sem mexer no backend.
  - ⚠️ Contratos de API precisam ser estáveis e bem documentados
    (OpenAPI ajuda) — ver [`11-contratos-api.md`](11-contratos-api.md).
  - ⚠️ Sem páginas server-rendered: catálogo é renderizado pelo frontend.

## ADR-006 — Empacotamento e ambientes

- **Decisão:** **Docker + Docker Compose** para todos os serviços (`backend`, `db`
  e, futuramente, `frontend`), cada um isolado.
- **Consequências:** `docker compose up` sobe o ambiente; paridade dev/prod.
  Detalhes em [`12-docker-e-ambientes.md`](12-docker-e-ambientes.md).

## ADR-007 — Autenticação

- **Contexto:** FastAPI não traz auth pronta. Precisamos autenticar o admin (P2) no MVP.
- **Decisão (proposta):** **OAuth2 Password Flow + JWT** (utilitários do próprio
  FastAPI), ou a biblioteca **fastapi-users** se quisermos contas de usuário prontas.
  → **Confirmar na implementação.** No MVP, basta autenticação de admin.
- **Consequências:**
  - ✅ Padrão; gratuito. JWT é stateless e simples para uma API.
  - ⚠️ Mais responsabilidade nossa sobre segurança (hash de senha, expiração de token).

## ADR-008 — Painel administrativo (substituto do Django Admin)

- **Contexto:** P2 precisa gerenciar produtos/pedidos no MVP, e não temos Django Admin.
- **Decisão (proposta):** **SQLAdmin** — painel administrativo gratuito para
  SQLAlchemy, integrável ao FastAPI. Entrega CRUD + autenticação com pouco esforço.
  - Alternativa: adiar e construir a administração no frontend separado (mais trabalho).
- **Consequências:**
  - ✅ MVP administrável sem depender do frontend.
  - ⚠️ Menos flexível que telas próprias; suficiente para o MVP.

## ADR-009 — Gerência de dependências

- **Decisão (proposta):** **uv** (rápido) **ou** pip + `requirements.txt` com versões
  fixadas. → Decidir na implementação; ambos gratuitos. Lockfile versionado.

## ADR-010 — Qualidade de código

- **Decisão:** **Ruff** (lint + format, PEP 8) e **pytest** + **pytest-asyncio** +
  **httpx** para testes (sem `pytest-django`). Detalhes em
  [`14-padroes-de-codigo.md`](14-padroes-de-codigo.md) e [`13-estrategia-de-testes.md`](13-estrategia-de-testes.md).

---

## Decisões em aberto

- [ ] Auth: JWT "na mão" vs **fastapi-users**.
- [ ] Admin: **SQLAdmin** vs construir no frontend.
- [ ] Driver Postgres **sync** (psycopg) vs **async** (asyncpg) → define se os services são async.
- [ ] uv vs pip.
- [ ] Versão exata de FastAPI/Starlette/Pydantic compatível com Python 3.14.5+.
