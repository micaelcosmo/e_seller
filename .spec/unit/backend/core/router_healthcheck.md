# Unit: router_healthcheck (`router`)

> Tipo: `router` · Área: `backend/core`
> Deriva de: [`planning/12`](../../../planning/12-docker-e-ambientes.md) §7 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Expor `GET /api/healthz` para o healthcheck do container/Compose.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/core/router_health.py` |
| Teste | `backend/tests/core/test_healthcheck.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api", tags=["health"])


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
```

- **Saída:** `200 {"status": "ok"}`.

## 4. Dependências

Nenhuma essencial (opcional: checar conexão com DB em versão "readiness").

## 5. Comportamento / regras

- Resposta rápida e barata.
- (Opcional) variante `readyz` que verifica o DB — fora do MVP.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | GET /api/healthz | `200` com `{"status":"ok"}` |

## 7. Rastreabilidade

- Planning [`12`](../../../planning/12-docker-e-ambientes.md) · Units: `core/app_factory`, `infra/docker_compose`

## 8. Pendências

- [ ] Incluir `readyz` (checagem de DB) agora ou depois?
