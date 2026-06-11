# Unit: CouponService (`service`)

> Tipo: `service` · Área: `backend/coupons` · Tier 🟡
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Validar um cupom e calcular o desconto; registrar o resgate de forma idempotente.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/coupons/services.py::CouponService` |
| Teste | `backend/tests/coupons/test_coupon_service.py` |

## 3. Contrato

```python
class CouponService:
    def __init__(self, session: Session, clock: Clock) -> None:
        self.session = session
        self.clock = clock

    def apply(self, code: str, amount: Decimal) -> Decimal:
        ...  # retorna valor com desconto; CouponInvalid se inativo/expirado/esgotado
    def redeem(self, code: str, order: Order) -> CouponRedemption:
        ...  # idempotente por order; CouponInvalid se inválido
```

## 4. Comportamento / regras

- Inválido se inativo, expirado (`valid_until`) ou esgotado (`max_redemptions`).
- `percent` aplica %, `fixed` subtrai; resultado nunca < 0.
- `redeem` é idempotente por pedido (UNIQUE `order_id`).
- Cálculo com operações explícitas (sem lambda).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Cupom percent válido | desconto correto |
| T2 | Cupom fixo > valor | resultado 0 (não negativo) |
| T3 | Expirado/esgotado/inativo | `CouponInvalid` |
| T4 | Resgate repetido no pedido | idempotente |

## 6. Rastreabilidade

- Units: `model_coupon`, `orders/service_create_order` (aplica no checkout)

## 7. Pendências

- [ ] Onde aplicar: na criação do pedido (congelar desconto no `amount`).
