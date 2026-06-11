# Unit: OrderStateMachine (`service`)

> Tipo: `service` · Área: `backend/orders`
> Deriva de: US-05 · RF-24 · RNF-21 · [`planning/09`](../../../planning/09-modelo-de-dominio.md) §3 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Garantir transições **válidas** de estado do pedido, rejeitando transições ilegais
e mantendo o estado consistente (RNF-21).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/orders/state_machine.py::OrderStateMachine` |
| Teste | `backend/tests/orders/test_state_machine.py` |

## 3. Contrato

```python
class OrderStateMachine:
    def __init__(self, order: Order) -> None:
        self.order = order

    def mark_paid(self) -> None: ...        # pending -> paid
    def mark_failed(self) -> None: ...      # pending -> failed
    def cancel(self) -> None: ...           # pending -> cancelled
    def refund(self) -> None: ...           # paid -> refunded
# Transição inválida levanta InvalidTransition.
```

- **Erros:** `InvalidTransition` para transições não permitidas.

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `model_order` (Order) | estado | real (objeto em memória) |

## 5. Comportamento / regras

Transições permitidas (ver [`planning/09`](../../../planning/09-modelo-de-dominio.md)):
- `pending → paid | failed | cancelled`
- `paid → refunded`
- Qualquer outra → `InvalidTransition` (ex.: `failed → paid`, `paid → paid` direto).
- Define o mapa de transições explicitamente (dict), sem comprehension.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | `pending` → `mark_paid` | vira `paid` |
| T2 | `pending` → `mark_failed` | vira `failed` |
| T3 | `paid` → `mark_paid` | `InvalidTransition` |
| T4 | `failed` → `mark_paid` | `InvalidTransition` |
| T5 | `paid` → `refund` | vira `refunded` |

## 7. Rastreabilidade

- US-05 · RF-24 · RNF-21 · Units: `model_order`, `payments/service_process_webhook`

## 8. Pendências

- [ ] Registrar histórico de transições (tabela de auditoria)?
