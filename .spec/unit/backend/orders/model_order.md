# Unit: Order / OrderItem (`model`)

> Tipo: `model` · Área: `backend/orders`
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md), [`planning/09`](../../../planning/09-modelo-de-dominio.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Mapear `order` e `order_item` (pedido multi-item; no MVP, 1 item por pedido).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/orders/models.py` (`Order`, `OrderItem`, `OrderStatus`) |
| Teste | `backend/tests/orders/test_model_order.py` |

## 3. Contrato

```python
class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid4)
    buyer_email: Mapped[str] = mapped_column(String(254))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)  # guest
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.PENDING)
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]


class OrderItem(Base):
    __tablename__ = "order_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # congelado
    quantity: Mapped[int] = mapped_column(default=1)
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/db_session` (Base) | mapeamento |
| `model_product`, `model_user` | FKs |

## 5. Comportamento / regras

- `reference` (UUID) é o identificador público (URLs), nunca o `id`.
- `unit_price` **congelado** no momento da compra (não muda com o produto).
- `amount` = soma dos itens.
- `user_id` nulável (guest checkout por `buyer_email`).
- E-book: `quantity = 1` (ver pendência de posse única em [`db/schema_overview`](../../db/schema_overview.md)).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Criar pedido com 1 item | persiste; `reference` único |
| T2 | `amount` ≠ soma dos itens | rejeitado/validado |
| T3 | Preço do produto muda depois | `unit_price` do item permanece |

## 7. Rastreabilidade

- RF-20,21 · [`db/schema_overview`](../../db/schema_overview.md) · Units: `service_create_order`, `service_state_machine`

## 8. Pendências

- [ ] CHECK `amount >= 0`; consistência amount × itens (no service ou trigger).
