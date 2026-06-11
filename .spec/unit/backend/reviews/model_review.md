# Unit: Review (`model`)

> Tipo: `model` · Área: `backend/reviews` · Tier 🟡
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Avaliação de produto (nota + comentário), idealmente de comprador verificado.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/reviews/models.py::Review` |
| Teste | `backend/tests/reviews/test_model_review.py` |

## 3. Contrato

```python
class Review(Base):
    __tablename__ = "review"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    rating: Mapped[int] = mapped_column()          # 1..5 (CHECK)
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime]
    # UNIQUE (product_id, user_id): uma review por usuário/produto
```

## 4. Comportamento / regras

- `rating` entre 1 e 5 (CHECK).
- UNIQUE (product, user) — uma avaliação por usuário/produto.
- "Comprador verificado": só quem tem `entitlement` do produto pode avaliar (regra no service).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Rating 0 ou 6 | viola CHECK |
| T2 | Segunda review do mesmo user | viola UNIQUE |

## 6. Rastreabilidade

- Units: `service_review`, `entitlement/model_entitlement` · Threat model (spam de review)

## 7. Pendências

- [ ] Moderação de comentários.
