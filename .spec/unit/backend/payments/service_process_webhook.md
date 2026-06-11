# Unit: WebhookProcessor (`service`)

> Tipo: `service`
> Área: `backend/payments`
> Deriva de: RF-23, RF-24 · RNF-01, RNF-02, RNF-11, RNF-20 · US-05 ·
> planning [`08`](../../../planning/08-arquitetura.md), [`09`](../../../planning/09-modelo-de-dominio.md),
> [`11`](../../../planning/11-contratos-api.md), [`18`](../../../planning/18-pagamentos-mercado-pago.md) · Status: **Rascunho (EXEMPLO)**
> Padrões: [`../../../standards/`](../../../standards/) — classe com DI no `__init__`, sem comprehension/lambda.

---

## 1. Objetivo

Processar uma notificação de pagamento do Mercado Pago de forma **idempotente**:
confirmar o pagamento na fonte (API do MP), atualizar o estado do pedido e, se
aprovado, disparar a emissão da entrega — **sem nunca duplicar efeitos** em
reentregas do webhook.

## 2. Localização (proposta)

| Item | Caminho |
|---|---|
| Código | `backend/app/payments/services.py::WebhookProcessor` |
| Teste | `backend/tests/payments/test_webhook_processor.py` |

## 3. Contrato (assinatura)

> Service como **classe com injeção de dependência** no `__init__` (SOLID/DIP).

```python
class WebhookProcessor:
    def __init__(
        self,
        gateway: PaymentGateway,          # abstração (Protocol), não a impl concreta
        session: Session,                 # sessão SQLAlchemy (transação)
        download_issuer: DownloadIssuer,  # emite o grant ao aprovar
    ) -> None:
        self.gateway = gateway
        self.session = session
        self.download_issuer = download_issuer

    def process(self, notification: WebhookNotification) -> WebhookResult:
        ...
# Não levanta exceção para webhook duplicado (idempotente → outcome ALREADY_PROCESSED).
# Levanta PaymentLookupError se a consulta ao gateway falhar de forma transitória
#   (o router traduz em status que faz o MP reenviar).
```

- **Entrada:** `notification` contém ao menos o `provider_payment_id`.
- **Saída:** `WebhookResult` com `outcome ∈ {APPLIED, ALREADY_PROCESSED, IGNORED}` e o `order_reference` afetado.
- **Erros:** `PaymentLookupError` (falha transitória ao consultar o MP).
- **Dependências do `__init__`:** `gateway` (Protocol `PaymentGateway`), `session`,
  `download_issuer` — todas injetadas, nunca instanciadas por dentro.

> 💡 A **validação de assinatura** NÃO é feita aqui — é responsabilidade da unit
> [`security/webhook_signature`](../../security/README.md) (dependency do router).
> Este service assume uma notificação já autenticada e foca na lógica de negócio.

## 4. Dependências

> Injetadas no `__init__` (DIP); o gateway é a abstração `PaymentGateway` (Protocol).

| Depende de | Para quê | Nos testes |
|---|---|---|
| `PaymentGateway.fetch_payment(id)` (impl: `gateway_mercadopago`) | Buscar o pagamento na fonte (não confiar no corpo) | **fake/mock** |
| `payments/service_map_status` | Mapear status MP → estado do pedido | real |
| `payments/model_payment` | Registrar pagamento; `provider_payment_id` único | real (DB de teste) |
| `orders/service_state_machine` | Transição de estado do pedido | real |
| `delivery/DownloadIssuer` | Emitir `DownloadGrant` ao aprovar | real (ou spy) |

## 5. Comportamento / regras

1. **Confirmar na fonte:** buscar o pagamento via `fetch_payment(provider_payment_id)`
   — nunca confiar apenas no payload recebido (RNF-02/segurança).
2. **Idempotência (RNF-20):** se já existe `Payment` processado com aquele
   `provider_payment_id`, retornar `ALREADY_PROCESSED` **sem** repetir efeitos.
   A unicidade de `provider_payment_id` no banco é a salvaguarda final (ver
   [`db/constraints`](../../db/README.md)).
3. **Mapear status** (`service_map_status`): `approved→paid`, `rejected→failed`,
   `pending/in_process→pending`, `cancelled→cancelled`, `refunded→refunded`.
4. **Aplicar transição** respeitando a máquina de estados ([`09`](../../../planning/09-modelo-de-dominio.md)):
   - `pending → paid`: registrar `Payment`, transicionar pedido e **emitir `DownloadGrant`**.
   - `pending → failed`: registrar `Payment`, transicionar pedido, **sem** grant.
   - Transição inválida (ex.: pedido já `paid`): tratar como idempotente/`IGNORED`.
5. **Persistência atômica:** registro do `Payment` + transição + grant na **mesma
   transação**; em caso de corrida, a violação de UNIQUE aborta o duplicado.
6. **Auditoria:** guardar `raw_payload`/`processed_at` no `Payment` (LGPD: ver retenção).
7. **Resposta rápida** (RNF-11): o caminho feliz deve ser curto (< 1 s).

## 6. Casos de teste (TDD) — escrever o **Red** primeiro

| # | Cenário (Gherkin curto) | Entrada | Resultado esperado |
|---|---|---|---|
| T1 | Dado pedido `pending`; Quando webhook **aprovado**; Então paga e emite grant | notificação approved | `APPLIED`; pedido `paid`; 1 `Payment`; 1 `DownloadGrant` |
| T2 | Dado pedido já pago pelo mesmo `provider_payment_id`; Quando o **mesmo** webhook chega de novo | notificação repetida | `ALREADY_PROCESSED`; nenhum novo `Payment`/grant (idempotência) |
| T3 | Dado pedido `pending`; Quando webhook **rejeitado** | notificação rejected | `APPLIED`; pedido `failed`; **sem** grant |
| T4 | Dado pedido `pending`; Quando `fetch_payment` falha (timeout) | gateway lança | `PaymentLookupError`; nada persistido (rollback) |
| T5 | Dois webhooks **idênticos concorrentes** | 2x em paralelo | apenas **um** efeito; o segundo vê UNIQUE e vira `ALREADY_PROCESSED` |
| T6 | Webhook approved para `provider_payment_id` desconhecido na nossa base | sem pedido correspondente | `IGNORED` (logado), sem efeito |
| T7 | Status `pending/in_process` | notificação pending | `APPLIED`/`IGNORED`; pedido permanece `pending`; sem grant |

> Mocka-se **apenas** o `gateway_mercadopago`; o banco é real (DB de teste com
> transação revertida). Ver [`tests/mercadopago_mock`](../../tests/README.md) e
> [`tests/conftest_db`](../../tests/README.md).

## 7. Rastreabilidade

- **Requisitos:** RF-23, RF-24 · RNF-01, RNF-02, RNF-11, RNF-20
- **User stories:** US-05
- **Planning:** [`08`](../../../planning/08-arquitetura.md) · [`09`](../../../planning/09-modelo-de-dominio.md) · [`11`](../../../planning/11-contratos-api.md) · [`18`](../../../planning/18-pagamentos-mercado-pago.md)
- **Units relacionadas:** `payments/gateway_mercadopago`, `payments/service_map_status`,
  `payments/model_payment`, `orders/service_state_machine`, `delivery/service_issue_download`,
  `security/webhook_signature`, `db/constraints`

## 8. Pendências / decisões

- [ ] Formato exato do payload/identificador do Mercado Pago (confirmar no sandbox).
- [ ] `IGNORED` vs erro quando o pedido não é encontrado (afeta retry do MP).
- [ ] Service **sync** ou **async** (depende do driver Postgres — ADR-003).
