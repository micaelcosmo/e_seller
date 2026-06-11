# e_seller — Portal de Venda de E-books

Portal de venda de e-books: vitrine SPA + API FastAPI + PostgreSQL, tudo em Docker.

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e em execução.
- Porta `48080` (API/vitrine), `48173` (frontend), `48088` (relatório) e `48432` (Postgres) livres.

## Subir tudo em Docker (modo rápido)

```powershell
# 1) Clone e entre no diretório
git clone <url-do-repo> e_seller
cd e_seller

# 2) (Opcional) crie um .env para sobrescrever defaults
# Exemplo de .env:
#   APP_ENV=prod
#   DATABASE_URL=postgresql+psycopg://e_seller:senha_segura@db:5432/e_seller2
#   APP_SECRET_KEY=troque-por-valor-aleatorio
#   ADMIN_EMAIL=admin@suaempresa.com
#   ADMIN_PASSWORD=senha_segura

# 3) Suba todos os serviços
docker compose up -d

# 4) Acompanhe os logs
docker compose logs -f backend
```

## Serviços e portas

| Serviço | URL local | Descrição |
|---|---|---|
| Frontend SPA | http://localhost:48173 | Vitrine do cliente |
| API (Swagger) | http://localhost:48080/docs | Documentação interativa |
| API (health) | http://localhost:48080/api/v1/healthz | Healthcheck |
| Admin (SQLAdmin) | http://localhost:48080/admin | Painel administrativo |
| Relatório | http://localhost:48088 | Backlog / progresso do projeto |
| Postgres | localhost:48432 | Banco de dados |

## Fluxo de deploy

1. `docker compose build` — reconstrói todas as imagens.
2. `docker compose up -d` — sobe (ou atualiza) os contêineres.
3. O backend aguarda o Postgres ficar saudável antes de iniciar (entrypoint.sh).
4. Na primeira execução, o banco é criado automaticamente (`create_all`) e os dados de exemplo são inseridos (seeds).

## Variáveis de ambiente importantes

| Variável | Padrão | Descrição |
|---|---|---|
| `APP_ENV` | `dev` | `dev` semeia dados; `prod` não semeia |
| `DATABASE_URL` | sqlite (dev) / postgres (Docker) | URL de conexão async |
| `APP_SECRET_KEY` | `dev-secret-change-me` | Chave JWT — **troque em produção** |
| `ADMIN_EMAIL` | `admin@e_seller.local` | E-mail do admin inicial |
| `ADMIN_PASSWORD` | `change-me-dev` | Senha do admin — **troque em produção** |
| `CORS_ORIGINS` | `""` (aceita tudo em dev) | Lista de origens separada por vírgula |
| `LOG_LEVEL` | `INFO` | Nível de log (DEBUG/INFO/WARNING/ERROR) |
| `DB_SLOW_QUERY_MS` | `0` (desativado) | Limiar (ms) para slow query log |
| `MERCADOPAGO_WEBHOOK_SECRET` | `""` | Segredo do webhook MP (modo real) |

## Desenvolvimento local (sem Docker)

```powershell
cd backend
uv sync                                  # instala deps via uv.lock
uv run python -m pytest tests/ -q        # testes
uv run ruff check app/ tests/            # lint
uv run uvicorn app.main:app --reload     # servidor de dev
```

## Arquitetura

```
e_seller/
├── backend/          # API FastAPI (Python 3.14+, SQLAlchemy async, PostgreSQL)
│   ├── app/          # Código de produção
│   ├── tests/        # Testes pytest async
│   ├── seeds/        # Dados de exemplo (JSON — sem hardcode)
│   └── entrypoint.sh # Aguarda DB → inicia uvicorn
├── frontend/         # SPA HTML/JS (sem build, sem framework)
├── report/           # Serviço de relatório (backlog.json → HTML)
└── docker-compose.yml
```

Documentação completa: [`.spec/`](.spec/) · Padrões: [`.spec/standards/`](.spec/standards/)
