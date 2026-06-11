# Unit: docker-compose.yml (`infra`)

> Tipo: `infra` · Área: `infra`
> Deriva de: [`planning/12`](../../planning/12-docker-e-ambientes.md) · RNF-40 ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Orquestrar `backend` + `db` (e futuramente `frontend`) para subir o ambiente com um comando.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `docker-compose.yml` (raiz) |
| Teste | smoke: `docker compose up` + `GET /api/healthz` |

## 3. Conteúdo (contrato)

- Serviço `db` (**PostgreSQL**) com volume `pgdata` e **healthcheck**.
- Serviço `backend` (FastAPI **async**) com `depends_on: db (service_healthy)`.
- Serviço `frontend` (Next.js) e, opcional, `dashboard` (UI da evolução).
- Volumes `ebook_files` (protegido) e `media` montados no backend.
- Variáveis via `.env`; banco via **`postgresql+asyncpg://...`**.

### Sketch (`docker-compose.yml`)

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports: ["48432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      retries: 10

  backend:
    build: ./backend
    env_file: ./backend/.env
    depends_on:
      db: { condition: service_healthy }
    ports: ["48080:8000"]
    volumes:
      - ebook_files:/app/storage/ebooks
      - media:/app/media
    # entrypoint roda "alembic upgrade head" antes de subir o servidor

  frontend:
    build: ./frontend
    depends_on: [backend]
    ports: ["48173:3000"]

volumes:
  pgdata:
  ebook_files:
  media:
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `dockerfile_backend` | imagem do backend |
| `volumes` | persistência/arquivos |
| `env_config` | variáveis |

## 5. Comportamento / regras

- Backend só sobe após o `db` saudável (ordem correta).
- `frontend` entra como serviço separado quando a tecnologia for decidida (ADR-005).
- **Portas não-padrão** (host) — ver [`ports.md`](ports.md): backend `48080:8000`,
  db `48432:5432`, frontend `48173:...`, dashboard `48088:...`. Internamente os
  serviços usam as portas padrão.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | `docker compose up` | sobe db + backend |
| T2 | Healthcheck | `GET /api/healthz` responde `200` |
| T3 | Ordem | backend espera db saudável |

## 7. Rastreabilidade

- RNF-40 · Planning [`12`](../../planning/12-docker-e-ambientes.md) · Units: `core/router_healthcheck`, `entrypoint`, `volumes`

## 8. Pendências

- [ ] `docker-compose.prod.yml` (override de produção).
