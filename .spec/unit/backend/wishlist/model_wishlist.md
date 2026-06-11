# Unit: Wishlist / WishlistItem (`model`)

> Tipo: `model` · Área: `backend/wishlist` · Tier 🔵
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Lista de desejos do usuário.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/wishlist/models.py` (`Wishlist`, `WishlistItem`) |
| Teste | `backend/tests/wishlist/test_model_wishlist.py` |

## 3. Contrato

```python
class Wishlist(Base):
    __tablename__ = "wishlist"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)


class WishlistItem(Base):
    __tablename__ = "wishlist_item"
    wishlist_id: Mapped[int] = mapped_column(ForeignKey("wishlist.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), primary_key=True)
```

## 4. Comportamento / regras

- Uma wishlist por usuário (`user_id` único).
- PK composta evita item duplicado.

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Adicionar produto | item criado |
| T2 | Adicionar duplicado | sem duplicar (PK composta) |

## 6. Rastreabilidade

- Units: `service_wishlist`, `router_wishlist`

## 7. Pendências

- [ ] Mover item da wishlist para o carrinho.
