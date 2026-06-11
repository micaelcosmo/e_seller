# Unit: configure_cors (`security`/config)

> Tipo: `security`/config · Área: `security`
> Deriva de: [`planning/08`](../../planning/08-arquitetura.md), [`19`](../../planning/19-seguranca-e-lgpd.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Configurar CORS para aceitar **somente** o domínio do frontend (serviços separados).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/security/cors.py::configure_cors` |
| Teste | `backend/tests/security/test_cors.py` |

## 3. Contrato

```python
def configure_cors(app: FastAPI, allowed_origins: list[str]) -> None:
    app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, ...)
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/config.app_allowed_origins` | origens permitidas |

## 5. Comportamento / regras

- Origens vêm de env (lista); **não** usar `*` em produção.
- Por ambiente: dev permissivo (localhost), prod restrito.
- Construção da lista com laço explícito (sem comprehension).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Origem permitida | resposta com header CORS |
| T2 | Origem não listada | sem permissão CORS |

## 7. Rastreabilidade

- Planning [`08`](../../planning/08-arquitetura.md), [`19`](../../planning/19-seguranca-e-lgpd.md) · Units: `core/app_factory`, `core/config`

## 8. Pendências

- [ ] Métodos/headers permitidos por ambiente.
