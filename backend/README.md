# e_seller — Backend (MVP)

API FastAPI do portal de venda de e-books. Implementa o **MVP (Tier 🟢)**:
catálogo → compra → pagamento (simulado, sem conta) → webhook idempotente → download seguro.

> Segue os padrões em [`../.spec/standards/`](../.spec/standards/): código em inglês,
> docstrings/comentários em pt-BR, services como classes com injeção de dependência,
> sem comprehension/lambda, etc.

## Stack

- Python 3.14 · FastAPI · SQLAlchemy 2 · Pydantic · Jinja2 (vitrine demo).
- **Banco:** SQLite por padrão (zero setup). Postgres/Docker previstos nas specs.
- **Pagamento:** provedor **fake** (simulador local) — não exige conta Mercado Pago.

## Como rodar (local)

```powershell
# 1) Dependências (uma vez)
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install fastapi "uvicorn[standard]" "sqlalchemy>=2" pydantic-settings jinja2 python-multipart
.\.venv\Scripts\python.exe -m pip install pytest pytest-asyncio httpx ruff   # dev

# 2) Subir o servidor (porta NÃO-padrão 48080)
powershell -ExecutionPolicy Bypass -File scripts\run_local.ps1
```

- Vitrine: <http://localhost:48080/>
- API docs (Swagger): <http://localhost:48080/docs>
- Healthcheck: <http://localhost:48080/api/v1/healthz>

## Publicar na internet (PC como servidor, sem conta/custo)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\serve_public.ps1
```

Isso baixa o `cloudflared` (se preciso), sobe o backend e abre um **Cloudflare quick
tunnel**, imprimindo uma URL `https://*.trycloudflare.com`. A URL é **temporária**
(muda a cada execução) e só funciona com o PC ligado. Para URL estável (ex.: webhook
real), use um túnel **nomeado** — ver [`../.spec/distribution/`](../.spec/distribution/).

## Testes e qualidade

```powershell
.\.venv\Scripts\python.exe -m pytest        # 22 testes
.\.venv\Scripts\python.exe -m ruff check app tests
```

## Endpoints principais (`/api/v1`)

| Método | Rota | Descrição |
|---|---|---|
| GET | `/healthz` | Healthcheck |
| GET | `/products` (`?q=`) | Lista publicados / busca |
| GET | `/products/{slug}` | Detalhe |
| POST | `/orders` | Cria pedido + checkout |
| GET | `/orders/{reference}` | Status do pedido |
| POST | `/webhooks/mercadopago` | Webhook (idempotente) |
| GET | `/download/{token}` | Download seguro (expira/limite) |

Vitrine demo (server-rendered): `/`, `/comprar`, `/pay/simulate/{ref}`, `/pedido/{ref}`.

## Estrutura

```
app/
├─ core/        config, db, clock, healthcheck
├─ catalog/     produtos e categorias
├─ orders/      pedido, itens, máquina de estados
├─ payments/    gateway (fake), checkout, webhook, status map
├─ delivery/    grant, validação, streaming
├─ security/    tokens seguros, storage protegido (anti path traversal)
├─ web/         vitrine demo + simulador de pagamento
├─ seeds.py     dados de exemplo (idempotente)
└─ main.py      create_app()
tests/          pytest (catalog, orders, webhook, download, security)
```

## Notas / próximos passos

- Migrations Alembic e Postgres estão especificados (rodamos com `create_all` + SQLite no MVP).
- Auth/admin (SQLAdmin), entitlement/biblioteca, cupons, RBAC etc. estão nas specs
  (`.spec/unit/`) e entram nos próximos marcos ([`../.spec/roadmap.md`](../.spec/roadmap.md)).
- Frontend Next.js (storefront separado) especificado em [`../.spec/frontend/`](../.spec/frontend/);
  hoje há uma vitrine demo embutida para validar o fluxo no ar.
