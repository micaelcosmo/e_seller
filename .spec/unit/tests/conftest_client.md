# Unit: conftest_client (`tests`/fixture)

> Tipo: `fixture` · Área: `tests`
> Deriva de: [`planning/13`](../../planning/13-estrategia-de-testes.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Fixture do client `httpx` sobre o app ASGI (sem subir servidor), com overrides de DI.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/tests/conftest.py` (`client`) |

## 3. Contrato

```python
@pytest.fixture
def client(db_session) -> Iterator[AsyncClient]:
    app = create_app(test_settings)
    # override Depends: get_session -> db_session, gateways -> fakes
    # httpx.AsyncClient(transport=ASGITransport(app=app))
    ...
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/app_factory` | app |
| `conftest_db` | sessão de teste |
| `mercadopago_mock` | gateway fake |

## 5. Comportamento / regras

- Usa `ASGITransport` (em memória, sem rede).
- Sobrescreve dependências (sessão, gateways) por fakes/teste.
- Base para os testes de router.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | GET /api/healthz via client | `200` |
| T2 | Overrides ativos | usa DB de teste e gateway fake |

## 7. Rastreabilidade

- Planning [`13`](../../planning/13-estrategia-de-testes.md) · Units: `conftest_db`, `mercadopago_mock`, todos os `router_*`

## 8. Pendências

- [ ] Client async vs sync (alinha com services).
