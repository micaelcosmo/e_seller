# Logging

> Trilha observability · e_seller · 2026-06-06

---

## 1. Formato

- **Logs estruturados** (JSON) com: timestamp, nível, evento, `correlation_id`,
  e contexto não-sensível (ex.: `order_reference`, `provider_payment_id`).
- Níveis: DEBUG (dev), INFO (eventos), WARNING, ERROR.

## 2. Eventos a registrar

| Evento | Nível | Contexto |
|---|---|---|
| Pedido criado | INFO | `order_reference`, valor |
| Webhook recebido/processado | INFO | `provider_payment_id`, outcome |
| Transição de estado do pedido | INFO | de→para |
| Download concedido/negado | INFO/WARNING | motivo (expirado/limite) |
| Falha de pagamento/gateway | ERROR | sem dados sensíveis |
| Tentativa de auth inválida | WARNING | sem senha/token |

## 3. O que **NÃO** logar

- ❌ Senhas, hashes, tokens (JWT/download), `raw_payload` completo.
- ❌ Dados pessoais além do mínimo (e-mail só quando necessário e com cautela — LGPD).
- ❌ Segredos/credenciais (RNF-04).

## 4. Correlation ID

- Gerar/propagar um `correlation_id` por requisição (middleware) para ligar logs
  de uma mesma operação. Base para o [`tracing.md`](tracing.md).

## 5. Implementação (proposta)

- Logger estruturado (ex.: `structlog` ou `logging` + JSON formatter) — open-source.
- Configurado no `core` (ver [`../unit/backend/core/app_factory.md`](../unit/backend/core/app_factory.md)).

## 6. Pendências

- [ ] Biblioteca de logging (structlog vs stdlib+JSON).
- [ ] Destino dos logs em produção (stdout → coletor).
