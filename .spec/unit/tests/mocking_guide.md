# Guia: Mock, Fake e Stub

> Guia de testes · Área: `tests` · 2026-06-06
> Quando e como simular dependências. Segue SOLID/DIP ([`../../standards/solid.md`](../../standards/solid.md)).

---

## 1. Princípio: prefira **fakes via Protocol**, não mocks mágicos

Como os services recebem dependências por **injeção no `__init__`** (DIP), trocamos a
implementação real por um **fake** que implementa o mesmo `Protocol`. Isso é mais
legível e seguro que `unittest.mock.patch`.

```python
class FakePaymentGateway:  # implementa PaymentGateway (Protocol)
    def __init__(self, *, payment_status: str = "approved") -> None:
        self.payment_status = payment_status

    def create_checkout(self, order) -> CheckoutData:
        return CheckoutData(checkout_url="https://fake/checkout")

    def fetch_payment(self, provider_payment_id: str) -> PaymentData:
        return PaymentData(id=provider_payment_id, status=self.payment_status)
```

Ver [`mercadopago_mock`](mercadopago_mock.md).

## 2. Vocabulário

| Termo | O que é | Uso aqui |
|---|---|---|
| **Fake** | Implementação simplificada e funcional | **padrão** (gateways, etc.) |
| **Stub** | Retorna respostas fixas | dados de fronteira |
| **Mock** | Verifica interações (foi chamado?) | só quando o *efeito* é a chamada |
| **Spy** | Observa chamadas mantendo o real | casos pontuais |

## 3. O que mockar (só as **fronteiras**)

- **Serviços externos:** Mercado Pago → `FakePaymentGateway` ou `respx`.
- **Tempo:** injetar `Clock` ou usar `freezegun` ([`time_control`](time_control.md)).
- **Aleatoriedade:** injetar `TokenFactory` determinístico ([`download_token`](../security/download_token.md)).
- **Sistema de arquivos:** usar `tmp_path` (pytest) em vez de mock.

## 4. O que **NÃO** mockar

- ❌ O **banco de dados**: usamos um DB de teste real com rollback ([`conftest_db`](conftest_db.md)).
  Mockar o ORM esconde bugs de query/constraint.
- ❌ A **lógica sob teste** (óbvio, mas comum por acidente).
- ❌ Schemas Pydantic / validações internas.

> 💡 Over-mock = testes que passam mas o sistema quebra. Mocke a borda, teste o miolo de verdade.

## 5. Mock de HTTP com `respx` (alternativa ao fake)

```python
import respx
from httpx import Response


@respx.mock
def test_fetch_payment_aprovado():
    respx.get(url__regex=r".*/v1/payments/123").mock(
        return_value=Response(200, json={"id": "123", "status": "approved"})
    )
    gateway = MercadoPagoGateway(access_token="x", environment="sandbox", http=real_http)

    pagamento = gateway.fetch_payment("123")

    assert pagamento.status == "approved"
```

## 6. `monkeypatch` para ambiente

Use para variáveis de ambiente/config, não para substituir objetos de domínio:

```python
def test_settings_le_env(monkeypatch):
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://...")
    settings = Settings()
    assert settings.app_secret_key == "test-secret"
```

## 7. Override de dependências do FastAPI

Nos testes de rota, troque os `Depends` por fakes via `app.dependency_overrides`
(montado no fixture `client` — ver [`conftest_client`](conftest_client.md)):

```python
app.dependency_overrides[get_payment_gateway] = lambda: FakePaymentGateway()
```

> Exceção pontual ao "sem lambda": override trivial de DI em teste. Se preferir,
> use uma função nomeada — mantém o padrão do projeto.

## 8. Relacionado

[`how_to_pytest`](how_to_pytest.md) · [`mercadopago_mock`](mercadopago_mock.md) ·
[`time_control`](time_control.md) · [`security_testing`](security_testing.md)
