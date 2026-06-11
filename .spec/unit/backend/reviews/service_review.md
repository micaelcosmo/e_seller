# Unit: ReviewService (`service`)

> Tipo: `service` · Área: `backend/reviews` · Tier 🟡
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Criar e listar avaliações, garantindo a regra de **comprador verificado**.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/reviews/services.py::ReviewService` |
| Teste | `backend/tests/reviews/test_review_service.py` |

## 3. Contrato

```python
class ReviewService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user: User, product_slug: str, rating: int, comment: str) -> Review:
        ...  # NotEntitled se não possui o produto; AlreadyReviewed se já avaliou
    def list_for_product(self, product_slug: str, *, limit: int = 20, offset: int = 0) -> list[Review]:
        ...
```

## 4. Comportamento / regras

- Só cria review se o usuário tem `entitlement` do produto (compra verificada).
- Uma review por (user, product) — senão `AlreadyReviewed`.
- Lista paginada; agregação de média pode ser derivada (service/consulta).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Comprador avalia | review criada |
| T2 | Não-comprador avalia | `NotEntitled` |
| T3 | Avaliar duas vezes | `AlreadyReviewed` |
| T4 | Listar | retorna reviews do produto |

## 6. Rastreabilidade

- Units: `model_review`, `entitlement/service_grant_entitlement`, `router_reviews`

## 7. Pendências

- [ ] Cálculo/cache de média de notas no produto.
