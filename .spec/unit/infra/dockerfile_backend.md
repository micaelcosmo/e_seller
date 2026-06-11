# Unit: backend.Dockerfile (`infra`)

> Tipo: `infra` · Área: `infra`
> Deriva de: [`planning/12`](../../planning/12-docker-e-ambientes.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Imagem Docker do backend FastAPI, reprodutível e enxuta.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/docker/backend.Dockerfile` |
| Teste | verificação via build no CI |

## 3. Conteúdo (contrato)

- Base `python:3.14.x-slim` (tag pinada — ver [`python-and-tooling`](../../standards/python-and-tooling.md)).
- Instala dependências a partir do lockfile (uv/pip) — camada cacheável.
- Copia o código; define usuário **não-root**.
- `ENTRYPOINT` → `entrypoint.sh`; `CMD` sobe o servidor.

## 4. Dependências

| Depende de | Para quê |
|---|---|
| lockfile de deps | instalação determinística |
| `entrypoint` | inicialização |
| `server_uvicorn_gunicorn` | comando de start |

## 5. Comportamento / regras

- Multi-stage opcional (build deps × runtime) para imagem menor.
- Sem segredos na imagem; só via env em runtime.
- `.dockerignore` exclui `.venv`, `.git`, `tests` (se desejado), etc.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | Build | imagem builda sem erro |
| T2 | Usuário | container roda como não-root |

## 7. Rastreabilidade

- Planning [`12`](../../planning/12-docker-e-ambientes.md) · Units: `entrypoint`, `server_uvicorn_gunicorn`, `docker_compose`

## 8. Pendências

- [ ] Multi-stage agora ou depois.
