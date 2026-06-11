# Unit: CartService (`service`)

> Tipo: `service` · Área: `backend/cart` · Tier 🟡
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Gerenciar itens do carrinho e calcular o total (preview).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/cart/services.py::CartService` |
| Teste | `backend/tests/cart/test_cart_service.py` |

## 3. Contrato

```python
class CartService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, user: User, product_slug: str) -> None: ...     # AlreadyOwned se possui
    def remove(self, user: User, product_slug: str) -> None: ...
    def total(self, user: User) -> Decimal: ...                   # soma dos preços atuais
    def items(self, user: User) -> list[Product]: ...
```

## 4. Comportamento / regras

- `add` idempotente; recusa produto já possuído (`AlreadyOwned`) — checa `entitlement`.
- `total` soma com laço explícito (sem comprehension).
- Carrinho não congela preço (isso ocorre no pedido).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Add + total | total correto |
| T2 | Produto possuído | `AlreadyOwned` |
| T3 | Remove | item some |

## 6. Rastreabilidade

- Units: `model_cart`, `entitlement/service_grant_entitlement`, `orders/service_create_order`
