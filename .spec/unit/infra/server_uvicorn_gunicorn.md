# Unit: server (Uvicorn/Gunicorn) (`infra`)

> Tipo: `infra` · Área: `infra`
> Deriva de: [`planning/12`](../../planning/12-docker-e-ambientes.md) · ADR-001 ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Definir como o app ASGI é servido em dev e em produção.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | comando no `entrypoint.sh` / `CMD` do Dockerfile |
| Teste | smoke |

## 3. Contrato

- **Dev:** `uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000`.
- **Prod:** `gunicorn -k uvicorn.workers.UvicornWorker app.main:create_app(...) --workers N`.

> Porta **interna** do container = 8000; exposição no **host** = `48080` (não-padrão),
> mapeada no Compose. Ver [`ports.md`](ports.md).

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/app_factory` (`create_app`) | aplicação ASGI |

## 5. Comportamento / regras

- `--reload` só em dev.
- Nº de workers configurável por env em prod.
- Logs estruturados; sem dados sensíveis.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | Subir em dev | responde em `:8000`, reload ativo |
| T2 | Subir em prod | múltiplos workers, sem reload |

## 7. Rastreabilidade

- ADR-001 · Planning [`12`](../../planning/12-docker-e-ambientes.md) · Units: `core/app_factory`, `entrypoint`

## 8. Pendências

- [ ] Nº de workers padrão; timeout/keepalive.
