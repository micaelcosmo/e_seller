# Unit: entrypoint.sh (`infra`)

> Tipo: `infra` · Área: `infra`
> Deriva de: [`planning/12`](../../planning/12-docker-e-ambientes.md) §7 ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Inicializar o container do backend: aguardar o DB, aplicar migrations e subir o servidor.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/docker/entrypoint.sh` |
| Teste | smoke via compose |

## 3. Conteúdo (contrato)

1. Aguardar o `db` aceitar conexões.
2. `alembic upgrade head`.
3. (dev) opcionalmente rodar seeds.
4. Iniciar o servidor (Uvicorn dev / Gunicorn prod — ver [`server_uvicorn_gunicorn`](server_uvicorn_gunicorn.md)).

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `db/alembic_setup` | migrations |
| `db/seeds` | dados de dev (opcional) |
| `server_uvicorn_gunicorn` | start |

## 5. Comportamento / regras

- Falhar cedo e claro se o DB não subir / migration falhar.
- Idempotente: `upgrade head` não reaplica o já aplicado.
- Seeds só em `APP_ENV=dev`.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | Subida normal | migra e inicia o servidor |
| T2 | DB indisponível | aguarda; falha clara se exceder timeout |

## 7. Rastreabilidade

- Planning [`12`](../../planning/12-docker-e-ambientes.md) · Units: `db/alembic_setup`, `server_uvicorn_gunicorn`

## 8. Pendências

- [ ] Estratégia de espera (healthcheck do compose vs script de wait).
