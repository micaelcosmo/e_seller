# 12 — Docker e Ambientes

> Documento de planning · e_seller · 2026-06-06 (revisado p/ FastAPI, serviços separados)
> Tudo em containers, custo zero, ambiente reprodutível (RNF-40,41,42).

---

## 1. Princípios

- **Tudo em Docker:** `backend`, `db` e (futuramente) `frontend`.
- **Backend e frontend são serviços independentes** (containers separados, possivelmente
  repositórios separados) — comunicação só por HTTP/JSON.
- `docker compose up` sobe o ambiente de desenvolvimento.
- **Paridade dev/prod:** mesma imagem base; diferenças via variáveis de ambiente.
- **Segredos** nunca no repositório — só via `.env` (ignorado) / cofre na produção.

## 2. Serviços previstos (Compose)

| Serviço | Imagem base | Papel | Porta |
|---|---|---|---|
| `backend` | `python:3.14-slim` (confirmar tag) | FastAPI + Uvicorn (dev) / Gunicorn+Uvicorn workers (prod) | 8000 |
| `db` | `postgres:<versão LTS>` | Banco de dados | 5432 (interno) |
| `frontend` | a definir | Frontend (quando ADR-005 fechar) | a definir |

> 💡 *Uvicorn vs Gunicorn:* FastAPI é **ASGI**, servido pelo **Uvicorn**. Em produção,
> roda-se **Gunicorn** gerenciando *workers* Uvicorn (mais robusto). A tag exata de
> Python 3.14 deve ser confirmada na implementação.

## 3. Estrutura de arquivos (proposta) — backend separado

```
backend/
├─ app/
│  ├─ core/        # config (pydantic-settings), db session, security (JWT), healthcheck
│  ├─ catalog/  orders/  payments/  delivery/  accounts/  admin/
│  └─ main.py     # cria o app FastAPI, inclui routers, monta SQLAdmin
├─ alembic/        # migrations
├─ alembic.ini
├─ tests/
├─ docker/
│  ├─ backend.Dockerfile
│  └─ entrypoint.sh        # espera o db + alembic upgrade + start
├─ pyproject.toml          # deps + Ruff + pytest
└─ .env.example

docker-compose.yml          # orquestra backend + db (e frontend quando existir)
docker-compose.prod.yml     # override de produção (futuro)
```

> O **frontend**, quando definido, terá sua própria pasta/repo e Dockerfile,
> referenciado no `docker-compose.yml`.

## 4. Volumes

| Volume | Propósito |
|---|---|
| `pgdata` | Persistência do PostgreSQL. |
| `ebook_files` | **Arquivos de e-book protegidos** (fora de qualquer rota estática pública). |
| `media` | Capas e estáticos públicos. |

> Os arquivos de e-book ficam em volume **separado e não servido estaticamente** —
> só a rota `/api/download/{token}` os entrega (ver [`20`](20-entrega-ebook-anti-pirataria.md)).

## 5. Variáveis de ambiente (contrato — `.env.example`)

```
# App / FastAPI
APP_ENV=dev
APP_SECRET_KEY=            # assinatura de JWT
APP_ALLOWED_ORIGINS=http://localhost:3000   # CORS (domínio do frontend)

# Banco
POSTGRES_DB=e_seller
POSTGRES_USER=e_seller
POSTGRES_PASSWORD=
DATABASE_URL=postgresql+psycopg://e_seller:...@db:5432/e_seller

# Mercado Pago
MP_ACCESS_TOKEN=
MP_WEBHOOK_SECRET=
MP_ENVIRONMENT=sandbox
```

## 6. Ambientes

| Ambiente | Descrição |
|---|---|
| **dev** | Local, `APP_ENV=dev`, Mercado Pago **sandbox**, dados de seed, `/docs` aberto. |
| **test** | CI; banco efêmero; Mercado Pago **mockado**. |
| **prod** | Segredos via cofre, HTTPS obrigatório, CORS restrito, Mercado Pago real. |

## 7. Healthcheck e inicialização

- Endpoint `GET /api/healthz` (módulo `core`) para checagem de saúde do container.
- `entrypoint.sh`: aguarda o `db`, roda **`alembic upgrade head`**, sobe Uvicorn/Gunicorn.
- Compose com `depends_on` + healthcheck do Postgres para ordem correta de subida.

## 8. Custo zero

Todas as peças (Python, FastAPI, Uvicorn, SQLAlchemy, Alembic, PostgreSQL, Docker,
Ruff, pytest, SQLAdmin, sandbox do Mercado Pago) são **gratuitas/open-source**.
Nenhum serviço pago é necessário para desenvolver e rodar o MVP localmente (RNF-42).

## 9. Pendências

- [ ] Tag exata da imagem Python 3.14 e versão do Postgres.
- [ ] Driver Postgres sync (`psycopg`) vs async (`asyncpg`) — afeta `DATABASE_URL` e os services.
- [ ] Servir estáticos/capas (volume + Nginx? CDN depois?).
- [ ] Hospedagem de produção mantendo custo baixo (definir no roadmap).
