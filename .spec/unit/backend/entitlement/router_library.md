# Unit: router_library (`router`)

> Tipo: `router` · Área: `backend/entitlement` · Tier 🟡
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

"Minha Biblioteca": e-books que o usuário possui, com acesso a (re)download.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/entitlement/router.py` |
| Teste | `backend/tests/entitlement/test_router_library.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/v1/library", tags=["library"])

@router.get("", response_model=list[ProductListItem])
def my_library(user: User = Depends(get_current_user), svc: EntitlementService = Depends(...)): ...

@router.post("/{slug}/download-link")   # reemite download_grant para um item possuído
def reissue_download(slug: str, user: User = Depends(get_current_user), ...): ...
```

## 4. Comportamento / regras

- Exige login (`401`).
- Reemissão de link só para produto **possuído** (`403` se não possui) — gera novo `DownloadGrant`.

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Library autenticada | lista posses |
| T2 | Reemitir link de item possuído | novo grant |
| T3 | Reemitir item não possuído | `403` |

## 6. Rastreabilidade

- Units: `service_grant_entitlement`, `delivery/service_issue_download`, `security/auth_dependency`
