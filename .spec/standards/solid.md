# SOLID

> Padrão · e_seller · 2026-06-06
> Os 5 princípios aplicados à arquitetura FastAPI + SQLAlchemy do e_seller.

---

## S — Single Responsibility (Responsabilidade Única)

Cada classe tem **um** motivo para mudar.
- Um **service** por caso de uso (ex.: `WebhookProcessor`, `OrderCreator`), não um "service deus".
- `router` cuida de HTTP; `service` cuida de regra; `model` cuida de persistência; `gateway` cuida de integração externa.

## O — Open/Closed (Aberto/Fechado)

Aberto para extensão, fechado para modificação.
- Novos meios de pagamento entram como **novas implementações** de um contrato (`PaymentGateway`),
  sem alterar o `WebhookProcessor`.

## L — Liskov Substitution (Substituição de Liskov)

Implementações de um contrato são intercambiáveis.
- Um `FakePaymentGateway` (testes) substitui o `MercadoPagoGateway` sem quebrar o service.

## I — Interface Segregation (Segregação de Interface)

Interfaces pequenas e focadas — use `typing.Protocol`.
```python
from typing import Protocol


class PaymentGateway(Protocol):
    def fetch_payment(self, payment_id: str) -> PaymentData: ...
    def create_checkout(self, order: Order) -> CheckoutData: ...
```
Não forçar um cliente a depender de métodos que não usa.

## D — Dependency Inversion (Inversão de Dependência)

Depender de **abstrações**, não de implementações. **Injeção via construtor** (`__init__`).
```python
class WebhookProcessor:
    def __init__(self, gateway: PaymentGateway, session: Session) -> None:
        self.gateway = gateway
        self.session = session
```
- O service recebe o `gateway` e a `session`; **não** os cria internamente.
- No FastAPI, a montagem das dependências fica nas `Depends(...)` do router.
- Isso torna tudo **testável** (injeta-se um fake) e está alinhado ao nosso padrão de POO.

## Resumo prático

- Services = **classes** com dependências no `__init__`.
- Integrações externas atrás de **Protocol**.
- Sem instanciar dependências "por dentro" (sem `MercadoPagoGateway()` dentro do service).
- Ver [`oop-and-naming.md`](oop-and-naming.md).
