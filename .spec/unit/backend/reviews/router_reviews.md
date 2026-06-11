# Unit: router_reviews (`router`)

> Tipo: `router` · Área: `backend/reviews` · Tier 🟡
> Deriva de: [`../../../api/endpoints.md`](../../../api/endpoints.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Expor criação (autenticada) e listagem (pública) de avaliações.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/reviews/router.py` |
| Teste | `backend/tests/reviews/test_router_reviews.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/v1/products/{slug}/reviews", tags=["reviews"])

@router.get("", response_model=list[ReviewOut])
def list_reviews(slug: str, svc: ReviewService = Depends(get_review_service)): ...

@router.post("", response_model=ReviewOut, status_code=201)
def create_review(slug: str, data: ReviewIn,
                  user: User = Depends(get_current_user),
                  svc: ReviewService = Depends(get_review_service)): ...
```

## 4. Comportamento / regras

- Criar exige login; `403/422` se não-comprador (`NotEntitled`)/duplicada.
- Listar é público.

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | GET reviews | `200` lista |
| T2 | POST sem login | `401` |
| T3 | POST não-comprador | `403` |
| T4 | POST válido | `201` |

## 6. Rastreabilidade

- Units: `service_review`, `security/auth_dependency` · API [`endpoints`](../../../api/endpoints.md)

## 7. Pendências

- [ ] Atualizar `api/endpoints.md` com estas rotas.
