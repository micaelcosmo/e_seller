# Unit: Coupon / CouponRedemption (`model`)

> Tipo: `model` · Área: `backend/coupons` · Tier 🟡
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Cupom de desconto e o registro de resgates (controle de uso).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/coupons/models.py` (`Coupon`, `CouponRedemption`) |
| Teste | `backend/tests/coupons/test_model_coupon.py` |

## 3. Contrato

```python
class DiscountType(str, Enum):
    PERCENT = "percent"
    FIXED = "fixed"


class Coupon(Base):
    __tablename__ = "coupon"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True)
    discount_type: Mapped[DiscountType]
    value: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    active: Mapped[bool] = mapped_column(default=True)
    valid_until: Mapped[datetime | None] = mapped_column(nullable=True)
    max_redemptions: Mapped[int | None] = mapped_column(nullable=True)


class CouponRedemption(Base):
    __tablename__ = "coupon_redemption"
    id: Mapped[int] = mapped_column(primary_key=True)
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupon.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), unique=True)
```

## 4. Comportamento / regras

- `code` único; `percent` (0–100) ou `fixed` (≥0) — CHECK conforme tipo.
- `CouponRedemption.order_id` único → um cupom por pedido; base de idempotência.
- Limite por `max_redemptions` e validade por `valid_until`.

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Code duplicado | viola UNIQUE |
| T2 | Dois resgates no mesmo pedido | viola UNIQUE |

## 6. Rastreabilidade

- Units: `service_coupon`, `orders/model_order` · Threat model (fraude de desconto)

## 7. Pendências

- [ ] Cupom por produto/categoria vs global.
