# Unit: lgpd_data_handling (`security`/política)

> Tipo: `security` (política) · Área: `security`
> Deriva de: RNF-05,06 · [`planning/19`](../../planning/19-seguranca-e-lgpd.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Definir o tratamento de dados pessoais conforme a LGPD: minimização, retenção e exclusão.

## 2. Localização

| Item | Caminho |
|---|---|
| Política/serviço | `backend/app/security/privacy.py` (ex.: `DataEraser`) |
| Teste | `backend/tests/security/test_lgpd.py` |

## 3. Contrato (serviço de exclusão)

```python
class DataEraser:
    def __init__(self, session: Session) -> None:
        self.session = session

    def erase_buyer(self, email: str) -> None:
        ...  # anonimiza buyer_email e remove payloads, preservando o mínimo legal
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `session` | atualizar/remover |
| `orders/model_order`, `payments/model_payment` | dados pessoais |

## 5. Comportamento / regras

- **Minimização:** coletar só `buyer_email` (RNF-05); não armazenar cartão (fica no MP).
- **Retenção:** `payment.raw_payload` e logs têm prazo de descarte.
- **Exclusão:** anonimizar `buyer_email`, remover payloads, preservando o mínimo fiscal/legal (RNF-06).
- Operação registrada em auditoria (sem vazar dados).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Exclusão a pedido | `buyer_email` anonimizado; payload removido |
| T2 | Preserva mínimo legal | registros fiscais essenciais mantidos |

## 7. Rastreabilidade

- RNF-05,06 · Planning [`19`](../../planning/19-seguranca-e-lgpd.md) · Units: `orders/model_order`, `payments/model_payment`

## 8. Pendências

- [ ] Definir prazos de retenção concretos.
- [ ] Política de privacidade/termos (texto jurídico).
