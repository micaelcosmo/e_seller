# Unit: BillingProfile (`model`)

> Tipo: `model` · Área: `backend/billing` · Tier 🔵
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md), [`planning/19`](../../../planning/19-seguranca-e-lgpd.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Dados fiscais do comprador para emissão de nota fiscal (NF) — produto digital.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/billing/models.py::BillingProfile` |
| Teste | `backend/tests/billing/test_model_billing_profile.py` |

## 3. Contrato

```python
class BillingProfile(Base):
    __tablename__ = "billing_profile"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)
    tax_id: Mapped[str] = mapped_column(String(20))      # CPF/CNPJ
    legal_name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime]
    # order referencia billing_profile (fatura com)
```

## 4. Comportamento / regras

- Dado pessoal/sensível (CPF) → minimização, segurança e retenção (LGPD).
- Vinculado a usuário (ou avulso por pedido para guest).
- Validar formato de CPF/CNPJ (no schema/service).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Criar perfil | persiste |
| T2 | CPF/CNPJ inválido | erro de validação |

## 6. Rastreabilidade

- RNF-05,06 · Units: `service_billing`, `orders/model_order` (FK) · ops [`lgpd-data-deletion`](../../../ops/lgpd-data-deletion.md)

## 7. Pendências

- [ ] Integração com provedor de NF-e/NFS-e.
- [ ] Criptografia em repouso do `tax_id`?
