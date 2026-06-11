# Tracing / Correlação

> Trilha observability · e_seller · 2026-06-06

---

## 1. Objetivo

Seguir uma operação ponta a ponta (request → service → DB → gateway) para diagnóstico.

## 2. Correlation ID

- Middleware gera um `correlation_id` por requisição (ou aceita um recebido).
- Propagado nos logs ([`logging.md`](logging.md)) e, idealmente, em chamadas ao gateway.

## 3. Tracing distribuído (futuro)

- **OpenTelemetry** (open-source) quando a complexidade justificar (backend + frontend
  separados + Mercado Pago). Fora do MVP.

## 4. Pendências

- [ ] Adotar OpenTelemetry agora (mínimo) ou só correlation_id no início?
