# Unit: Entitlement (`model`)

> Tipo: `model` · Área: `backend/entitlement` · Tier 🟡
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

**Posse perpétua** de um e-book por um usuário (distinta do link temporário de download).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/entitlement/models.py::Entitlement` |
| Teste | `backend/tests/entitlement/test_model_entitlement.py` |

## 3. Contrato

```python
class Entitlement(Base):
    __tablename__ = "entitlement"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_item.id"))
    created_at: Mapped[datetime]
    # UNIQUE (user_id, product_id): posse única do e-book
```

## 4. Comportamento / regras

- **UNIQUE (user, product)** → impede possuir/comprar o mesmo e-book duas vezes
  (resolve a pendência de posse única do [`schema_overview`](../../db/schema_overview.md)).
- Criado quando o `order_item` é pago (ver `service_grant_entitlement`).
- Base de "Minha Biblioteca" e de "comprador verificado" para reviews.

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Conceder posse | criada |
| T2 | Mesma posse de novo | viola UNIQUE (idempotente no service) |

## 6. Rastreabilidade

- Units: `service_grant_entitlement`, `reviews/service_review`, `cart/service_cart`

## 7. Pendências

- [ ] Posse para guest (sem user)? Vincular no "claim" da conta.
