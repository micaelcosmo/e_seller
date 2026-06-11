# Métricas

> Trilha observability · e_seller · 2026-06-06
> Liga as métricas aos KPIs de [`../planning/01-visao-de-produto.md`](../planning/01-visao-de-produto.md) §6.

---

## 1. Métricas de negócio

| Métrica | O que mede | Meta (planning) |
|---|---|---|
| Conversão | compras / visitantes | acompanhar |
| Pagamentos aprovados | approved / iniciados | — |
| Taxa de entrega | downloads válidos / pagamentos aprovados | ~100% |
| Tempo até download | aprovação → 1º download | < 1 min |
| Falhas de pagamento (técnicas) | erros / checkouts | < 1% |

## 2. Métricas técnicas

| Métrica | O que mede |
|---|---|
| Latência das rotas | p50/p95 por endpoint (RNF-10) |
| Webhooks: recebidos/processados/duplicados/erros | saúde do pagamento |
| Downloads: concedidos/negados (por motivo) | entrega/anti-pirataria |
| Erros 5xx | estabilidade |
| Saúde do DB/conexões | capacidade |

## 3. Implementação (proposta)

- Expor `/metrics` (Prometheus, open-source) ou contadores simples no início.
- Sem cardinalidade explosiva (não usar dados pessoais como label).

## 4. Pendências

- [ ] Stack de métricas (Prometheus/Grafana?) mantendo custo baixo.
- [ ] Instrumentação mínima no MVP vs depois.
