# Guia: Como escrever testes (pytest)

> Guia de testes · Área: `tests` · 2026-06-06
> Como escrevemos testes no e_seller. Segue [`../../standards/`](../../standards/) e
> [`test_conventions`](test_conventions.md). Os trechos são **exemplos ilustrativos**.

---

## 1. Onde os testes vivem

A pasta `tests/` **espelha** a estrutura de `app/`:

```
backend/
├─ app/payments/services.py        →  backend/tests/payments/test_webhook_processor.py
├─ app/catalog/services.py         →  backend/tests/catalog/test_list_products.py
├─ app/security/jwt.py             →  backend/tests/security/test_jwt.py
└─ tests/
   ├─ conftest.py                  # fixtures globais (ver conftest_db, conftest_client)
   ├─ factories.py                 # ver factories.md
   ├─ fakes/                       # fakes de fronteira (ver mocking_guide.md)
   └─ e2e/                         # fluxo ponta a ponta (ver e2e_purchase_flow.md)
```

> Cada **unit spec** aponta o caminho do seu teste na seção 2 ("Localização").

## 2. Anatomia de um teste — Arrange / Act / Assert

```python
def test_lista_apenas_produtos_publicados(db_session):
    # Arrange
    ProductFactory(status=ProductStatus.PUBLISHED)
    ProductFactory(status=ProductStatus.PUBLISHED)
    ProductFactory(status=ProductStatus.DRAFT)
    catalog = ProductCatalog(session=db_session)

    # Act
    publicados = catalog.list_published()

    # Assert
    assert len(publicados) == 2
```

- **Nome descritivo** do comportamento (não `test_1`) — ver [`test_conventions`](test_conventions.md).
- Um conceito por teste. Asserts claros.
- **Sem comprehension/lambda** também no teste (padrão do projeto).

## 3. Fixtures

- `db_session`: sessão de teste com rollback por teste — ver [`conftest_db`](conftest_db.md).
- `client`: client httpx sobre o app ASGI — ver [`conftest_client`](conftest_client.md).
- Factories para dados — ver [`factories`](factories.md).
- Tempo determinístico — ver [`time_control`](time_control.md).

```python
def test_download_valido_incrementa_contador(db_session, frozen_clock):
    grant = DownloadGrantFactory(download_count=0)
    validator = GrantValidator(session=db_session, clock=frozen_clock)

    consumido = validator.consume(grant.token)

    assert consumido.download_count == 1
```

## 4. Parametrização (vários casos, um teste)

```python
import pytest


@pytest.mark.parametrize(
    "provider_status, esperado",
    [
        ("approved", OrderStatus.PAID),
        ("rejected", OrderStatus.FAILED),
        ("in_process", OrderStatus.PENDING),
    ],
)
def test_mapeia_status_do_provedor(provider_status, esperado):
    assert map_provider_status(provider_status) == esperado
```

## 5. Marcadores (markers)

Classificar para rodar seletivamente:

```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.e2e
```

- **unit:** regra pura/serviço isolado (rápido).
- **integration:** envolve DB/rota.
- **e2e:** fluxo completo (ver [`e2e_purchase_flow`](e2e_purchase_flow.md)).

## 6. Testes assíncronos

Com `asyncio_mode=auto` ([`pytest_config`](pytest_config.md)):

```python
async def test_get_healthz(client):
    resposta = await client.get("/api/healthz")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}
```

## 7. Testando exceções

```python
def test_produto_rascunho_nao_e_encontrado(db_session):
    ProductFactory(slug="oculto", status=ProductStatus.DRAFT)
    catalog = ProductCatalog(session=db_session)

    with pytest.raises(ProductNotFound):
        catalog.get_by_slug("oculto")
```

## 8. O ciclo TDD na prática (Red → Green → Refactor)

1. Pegue um cenário da seção 6 da unit spec.
2. Escreva o teste → roda e **falha** (Red).
3. Implemente o mínimo → teste **passa** (Green).
4. Refatore mantendo verde.

## 9. O que NÃO fazer

- ❌ Testar detalhes de implementação (só comportamento observável).
- ❌ Depender de ordem entre testes ou de rede real.
- ❌ `time.sleep`/relógio real — use [`time_control`](time_control.md).
- ❌ Mockar o que não é fronteira (ver [`mocking_guide`](mocking_guide.md)).

## 10. Relacionado

[`mocking_guide`](mocking_guide.md) · [`security_testing`](security_testing.md) ·
[`io_testing`](io_testing.md) · [`test_conventions`](test_conventions.md)
