# Unit: router_coupons (`router`)

> Tipo: `router` · Área: `backend/coupons` · Tier 🟡
> Deriva de: [`../../../api/endpoints.md`](../../../api/endpoints.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Validar cupom (público, no checkout) e CRUD de cupons (admin).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/coupons/router.py` |
| Teste | `backend/tests/coupons/test_router_coupons.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/v1/coupons", tags=["coupons"])

@router.post("/validate")     # público: aplica ao valor e retorna preview do desconto
def validate(data: CouponValidateIn, svc: CouponService = Depends(get_coupon_service)): ...
# CRUD administrativo via SQLAdmin (CouponAdmin) ou rotas protegidas por require_role("admin").
```

## 4. Comportamento / regras

- `validate` retorna desconto/total; `422/404` se inválido.
- Criação/edição de cupom exige papel admin (`require_role`).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Validar cupom ativo | retorna desconto |
| T2 | Cupom inválido | erro |
| T3 | Criar cupom sem admin | `403` |

## 6. Rastreabilidade

- Units: `service_coupon`, `security/rbac_authorization` · API [`endpoints`](../../../api/endpoints.md)

## 7. Pendências

- [ ] Atualizar `api/endpoints.md`.
