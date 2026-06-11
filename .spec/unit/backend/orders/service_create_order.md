# Unit: OrderCreator (`service`)

> Tipo: `service` · Área: `backend/orders`
> Deriva de: US-04 · RF-20,21,22 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Criar um pedido `pending` (congelando o preço) e iniciar o checkout no Mercado Pago.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/orders/services.py::OrderCreator` |
| Teste | `backend/tests/orders/test_create_order.py` |

## 3. Contrato

```python
class OrderCreator:
    def __init__(self, session: Session, checkout: CheckoutService) -> None:
        self.session = session
        self.checkout = checkout

    def create(self, product_slug: str, buyer_email: str) -> Order:
        ...  # levanta ProductNotFound se produto não publicado
```

- **Saída:** `Order` `pending` com `checkout_url` definido.
- **Erros:** `ProductNotFound` (404).

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `session` | persistência | real |
| `catalog` (get_by_slug) | validar produto | real |
| `payments/CheckoutService` | gerar `checkout_url` | **fake** |

## 5. Comportamento / regras

- Produto deve estar `published`; senão `ProductNotFound`.
- Cria `OrderItem` com `unit_price` = preço atual (**congelado**); `amount` = total.
- Estado inicial `pending`.
- Chama o checkout e guarda a `checkout_url`.
- Persistência atômica (pedido + item).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Produto publicado | cria pedido `pending` + item, retorna `checkout_url` |
| T2 | Produto rascunho/inexistente | `ProductNotFound` |
| T3 | Preço congelado | item guarda preço do momento |
| T4 | Falha no checkout | pedido não fica inconsistente (rollback ou pending sem url + erro tratado) |

## 7. Rastreabilidade

- US-04 · RF-20,21,22 · Units: `model_order`, `payments/service_create_checkout`, `catalog/service_get_product`

## 8. Pendências

- [ ] Reaproveitar pedido `pending` existente para o mesmo e-mail/produto?
