# Unit: Cart / CartItem (`model`)

> Tipo: `model` · Área: `backend/cart` · Tier 🟡
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Carrinho do usuário (compra multi-item antes do pedido).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/cart/models.py` (`Cart`, `CartItem`) |
| Teste | `backend/tests/cart/test_model_cart.py` |

## 3. Contrato

```python
class Cart(Base):
    __tablename__ = "cart"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)


class CartItem(Base):
    __tablename__ = "cart_item"
    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), primary_key=True)
    # quantity = 1 para e-book (posse única) — ver schema_overview pendência
```

## 4. Comportamento / regras

- Um carrinho por usuário; item único por produto (PK composta).
- E-book: quantidade efetiva 1 (posse única — `entitlement`).
- Não duplicar produto já possuído (validar no service).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Adicionar item | persiste |
| T2 | Produto já no carrinho | sem duplicar |

## 6. Rastreabilidade

- Units: `service_cart`, `orders/service_create_order` (checkout a partir do carrinho)

## 7. Pendências

- [ ] Bloquear adicionar produto já possuído (`entitlement`).
