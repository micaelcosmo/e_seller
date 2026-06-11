# Unit: router_wishlist (`router`)

> Tipo: `router` · Área: `backend/wishlist` · Tier 🔵
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Endpoints autenticados da wishlist do usuário.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/wishlist/router.py` |
| Teste | `backend/tests/wishlist/test_router_wishlist.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/v1/wishlist", tags=["wishlist"])

@router.get("", response_model=list[ProductListItem])
def list_wishlist(user: User = Depends(get_current_user), svc: WishlistService = Depends(...)): ...

@router.post("/{slug}", status_code=204)
def add(slug: str, user: User = Depends(get_current_user), svc: WishlistService = Depends(...)): ...

@router.delete("/{slug}", status_code=204)
def remove(slug: str, user: User = Depends(get_current_user), svc: WishlistService = Depends(...)): ...
```

## 4. Comportamento / regras

- Todas exigem login (`401` sem token).
- `204` para add/remove; `200` lista.

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Add autenticado | `204`, aparece na lista |
| T2 | Sem login | `401` |
| T3 | Remove | `204` |

## 6. Rastreabilidade

- Units: `service_wishlist`, `security/auth_dependency` · API [`endpoints`](../../../api/endpoints.md)
