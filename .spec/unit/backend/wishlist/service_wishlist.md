# Unit: WishlistService (`service`)

> Tipo: `service` · Área: `backend/wishlist` · Tier 🔵
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Adicionar/remover/listar itens da wishlist do usuário.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/wishlist/services.py::WishlistService` |
| Teste | `backend/tests/wishlist/test_wishlist_service.py` |

## 3. Contrato

```python
class WishlistService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, user: User, product_slug: str) -> None: ...
    def remove(self, user: User, product_slug: str) -> None: ...
    def list_items(self, user: User) -> list[Product]: ...
```

## 4. Comportamento / regras

- Cria a wishlist do usuário sob demanda (se não existir).
- `add` idempotente (não duplica).
- Listagem com laço explícito (sem comprehension).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Add + list | item aparece |
| T2 | Add duplicado | idempotente |
| T3 | Remove | item some |

## 6. Rastreabilidade

- Units: `model_wishlist`, `router_wishlist`
