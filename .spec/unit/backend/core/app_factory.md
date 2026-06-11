# Unit: create_app (`app_factory`)

> Tipo: `app_factory` · Área: `backend/core`
> Deriva de: [`planning/08`](../../../planning/08-arquitetura.md), [`11`](../../../planning/11-contratos-api.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Construir a aplicação FastAPI: incluir routers, configurar CORS, montar o painel
SQLAdmin e registrar healthcheck. Função de composição (sem estado global).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/main.py::create_app` |
| Teste | `backend/tests/core/test_app_factory.py` |

## 3. Contrato

```python
def create_app(settings: Settings | None = None) -> FastAPI:
    app = FastAPI(title="e_seller API")
    # configura CORS (security/cors)
    # inclui routers: catalog, orders, payments, delivery, accounts, core/health
    # monta SQLAdmin (admin/sqladmin_setup)
    return app
```

- **Saída:** instância `FastAPI` pronta.
- **Erros:** falha de config aborta a criação.

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| routers de cada módulo | registrar rotas | real |
| `security/cors` | middleware CORS | real |
| `admin/sqladmin_setup` | montar painel | real (ou skip) |
| `core/config` | settings | injetado |

## 5. Comportamento / regras

- Recebe `settings` por parâmetro (testável); usa `get_settings()` se omitido.
- Ordem: middlewares → routers → admin.
- `/docs` e `/openapi.json` ativos conforme ambiente (restritos em prod — [`security`](../../security/README.md)).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | App criada | retorna `FastAPI` com rotas esperadas registradas |
| T2 | Healthcheck registrado | `GET /api/healthz` existe |
| T3 | CORS | origem permitida responde com header CORS |

## 7. Rastreabilidade

- Planning [`08`](../../../planning/08-arquitetura.md), [`11`](../../../planning/11-contratos-api.md)
- Units: todos os `router_*`, `security/cors`, `admin/sqladmin_setup`

## 8. Pendências

- [ ] Versionamento `/api/v1` (decidir no contrato).
