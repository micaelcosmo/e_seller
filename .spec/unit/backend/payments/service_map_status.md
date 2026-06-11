# Unit: StatusMapper (`service`)

> Tipo: `service` (mapeamento) · Área: `backend/payments`
> Deriva de: [`planning/18`](../../../planning/18-pagamentos-mercado-pago.md) §4 · RF-24 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Mapear o status do Mercado Pago para o `OrderStatus` interno.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/payments/status_map.py::StatusMapper` |
| Teste | `backend/tests/payments/test_status_mapper.py` |

## 3. Contrato

```python
class StatusMapper:
    """Traduz o status do provedor (Mercado Pago) para o OrderStatus interno."""

    _MAP = {  # constante de classe (dict explícito), sem comprehension
        "approved": OrderStatus.PAID,
        "pending": OrderStatus.PENDING,
        "in_process": OrderStatus.PENDING,
        "rejected": OrderStatus.FAILED,
        "cancelled": OrderStatus.CANCELLED,
        "refunded": OrderStatus.REFUNDED,
        "charged_back": OrderStatus.REFUNDED,
    }

    def to_order_status(self, provider_status: str) -> OrderStatus:
        """Retorna o OrderStatus; levanta UnknownProviderStatus se não mapeado."""
        ...
```

> Implementado como **classe** (cumpre "sem arquivo só com funções") com `_MAP` explícito.

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `orders/model_order.OrderStatus` | destino do mapa |

## 5. Comportamento / regras

| MP | Interno |
|---|---|
| `approved` | `PAID` |
| `pending`/`in_process` | `PENDING` |
| `rejected` | `FAILED` |
| `cancelled` | `CANCELLED` |
| `refunded`/`charged_back` | `REFUNDED` |

- Status desconhecido → `UnknownProviderStatus` (logar e tratar com cautela).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | `approved` | `PAID` |
| T2 | `rejected` | `FAILED` |
| T3 | `in_process` | `PENDING` |
| T4 | valor desconhecido | `UnknownProviderStatus` |

## 7. Rastreabilidade

- RF-24 · Planning [`18`](../../../planning/18-pagamentos-mercado-pago.md) · Units: `service_process_webhook`, `orders/service_state_machine`

## 8. Pendências

- [ ] Tratar `charged_back` separadamente de `refunded`?
