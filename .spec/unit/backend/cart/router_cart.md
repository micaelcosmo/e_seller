# Unit: router_cart (`router`)

> Tipo: `router` · Área: `backend/cart` · Tier 🟡
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Endpoints autenticados do carrinho.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/cart/router.py` |
| Teste | `backend/tests/cart/test_router_cart.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/v1/cart", tags=["cart"])

@router.get("")                      # itens + total
@router.post("/{slug}", status_code=204)
@router.delete("/{slug}", status_code=204)
# todos: user = Depends(get_current_user)
```

## 4. Comportamento / regras

- Exigem login (`401` sem token).
- Add de produto já possuído → `409/422` (`AlreadyOwned`).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Add autenticado | `204` |
| T2 | Sem login | `401` |
| T3 | Produto possuído | `409/422` |

## 6. Rastreabilidade

- Units: `service_cart`, `security/auth_dependency` · API [`endpoints`](../../../api/endpoints.md)
