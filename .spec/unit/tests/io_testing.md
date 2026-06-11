# Guia: Testes de Funcionalidade (I/O)

> Guia de testes · Área: `tests` · 2026-06-06
> Como testar entrada/saída: rotas da API, persistência, arquivos e contratos.
> Os trechos são exemplos ilustrativos.

---

## 1. Princípio

Testar o sistema pelas **bordas observáveis**: o que entra (request, dados) e o que
sai (response, persistência, arquivo). Caminho feliz **e** caminhos de erro/borda.

## 2. Rotas da API (httpx sobre ASGI)

Usar o fixture `client` ([`conftest_client`](conftest_client.md)); validar **status
code**, **corpo** e **efeito**.

```python
async def test_criar_pedido_retorna_201_e_checkout(client, db_session):
    ProductFactory(slug="ebook", status=ProductStatus.PUBLISHED, price=Decimal("39.90"))

    resposta = await client.post(
        "/api/orders",
        json={"product_slug": "ebook", "buyer_email": "leitor@x.com"},
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status"] == "pending"
    assert corpo["checkout_url"]
```

### Códigos a cobrir
| Código | Quando | Exemplo |
|---|---|---|
| 200/201 | sucesso | listar/criar |
| 422 | validação Pydantic | e-mail inválido |
| 404 | recurso ausente | produto/pedido inexistente |
| 401/403 | auth/autorização | rota admin sem token |
| 410/429 | grant expirado/limite | download |

```python
async def test_email_invalido_retorna_422(client):
    resposta = await client.post(
        "/api/orders", json={"product_slug": "x", "buyer_email": "nao-email"}
    )
    assert resposta.status_code == 422
```

## 3. Persistência (DB real de teste)

Sem mockar o banco — validar que dados e **constraints** funcionam.

```python
def test_provider_payment_id_e_unico(db_session):
    PaymentFactory(provider_payment_id="MP-1")
    with pytest.raises(IntegrityError):
        PaymentFactory(provider_payment_id="MP-1")
        db_session.flush()
```

```python
def test_preco_congelado_no_item(db_session):
    produto = ProductFactory(price=Decimal("39.90"))
    creator = OrderCreator(db_session, FakeCheckout())
    pedido = creator.create(produto.slug, "leitor@x.com")

    produto.price = Decimal("99.90")  # muda depois
    db_session.flush()

    assert pedido.items[0].unit_price == Decimal("39.90")
```

## 4. Arquivos / streaming

Usar `tmp_path`; validar conteúdo e cabeçalhos, sem expor caminho.

```python
def test_stream_retorna_conteudo_do_arquivo(tmp_path):
    arquivo = tmp_path / "livro.pdf"
    arquivo.write_bytes(b"%PDF-conteudo")
    streamer = FileStreamer(storage_root=tmp_path)

    info = streamer.open_stream(ProductStub(file="livro.pdf"))

    assert b"".join(info.chunks) == b"%PDF-conteudo"
    assert info.mimetype == "application/pdf"
```

## 5. Contratos (request/response)

- A saída segue o schema Pydantic (`ProductOut` **não** expõe `file`).
- Campos obrigatórios/opcionais conforme o contrato ([`planning/11`](../../planning/11-contratos-api.md)).

```python
async def test_produto_nao_expoe_arquivo(client):
    ProductFactory(slug="ebook", status=ProductStatus.PUBLISHED)
    corpo = (await client.get("/api/products/ebook")).json()
    assert "file" not in corpo
```

## 6. Bordas e erros

- Listas vazias, paginação (`limit`/`offset`), valores-limite.
- Caminhos de erro tão importantes quanto o feliz.
- Idempotência onde aplicável (ver [`security_testing`](security_testing.md)).

## 7. Boas práticas

- Um comportamento por teste; nome descritivo (AAA).
- Preferir asserts específicos (status + campo) a "não deu erro".
- Dados via factories ([`factories`](factories.md)); tempo via [`time_control`](time_control.md).
- Sem comprehension/lambda; laços explícitos quando montar dados.

## 8. Relacionado

[`how_to_pytest`](how_to_pytest.md) · [`security_testing`](security_testing.md) ·
[`e2e_purchase_flow`](e2e_purchase_flow.md) · planning [`11`](../../planning/11-contratos-api.md)
