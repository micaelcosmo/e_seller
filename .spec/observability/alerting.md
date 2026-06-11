# Alertas

> Trilha observability · e_seller · 2026-06-10
> Alertas acionáveis ligados a [`metrics.md`](metrics.md) e a
> [`../ops/incident-response.md`](../ops/incident-response.md).

---

## 1. Alertas prioritários

| Alerta | Condição | Limiar | Severidade | Endpoint de verificação |
|---|---|---|---|---|
| Pedidos pagos sem entrega | `order.status=PAID` sem `download_grant` | ≥ 1 | **alta** | `GET /api/v1/admin/alerts/check` |
| Taxa de erro de pagamento | `payment.status in (rejected, cancelled, failed)` / total | > 20% | **alta** | `GET /api/v1/admin/alerts/check` |
| Erros 5xx | HTTP 5xx / total requisições | > 1% por 5 min | **alta** | log JSON (`level=ERROR`) |
| Latência alta | p95 tempo de resposta | > 500 ms sustentado | **média** | slow query log (`DB_SLOW_QUERY_MS`) |
| Healthcheck falhando | `GET /api/v1/healthz` não retorna 200 | qualquer falha | **alta** | Docker healthcheck |
| DB indisponível | Conexão ao Postgres falha | qualquer falha | **alta** | entrypoint.sh (30 tentativas) |

---

## 2. Endpoint de verificação — `GET /api/v1/admin/alerts/check`

Retorna o estado atual dos alertas que podem ser verificados programaticamente:

```json
{
  "ok": false,
  "alerts": [
    {
      "name": "pagamentos_sem_entrega",
      "severity": "alta",
      "detail": "2 pedido(s) pago(s) sem grant de download."
    }
  ]
}
```

- Requer papel `staff` ou `admin`.
- Implementado em `app/core/router_alerts.py` → `AlertChecker`.
- Pode ser chamado por um monitor externo (Uptime Kuma, etc.) com autenticação.

---

## 3. Princípios

- Alerta deve ser **acionável** (tem runbook associado) — evitar fadiga de alerta.
- Cada alerta aponta para [`../ops/incident-response.md`](../ops/incident-response.md).
- Sem dados pessoais nas notificações (usar IDs, não e-mails).
- `ok=true` = sistema saudável; `ok=false` = investigar imediatamente.

---

## 4. Integração sugerida

- **Uptime Kuma**: monitorar `/api/v1/healthz` (HTTP 200) e `/api/v1/admin/alerts/check` (`ok=true`).
- **Logs JSON**: filtrar `"level":"ERROR"` para detectar 5xx em tempo real.
- **Slow query**: ativar `DB_SLOW_QUERY_MS=200` em produção para registrar queries lentas.

---

## 5. Changelog

- **2026-06-10**: Endpoint `AlertChecker` implementado; limiares concretos definidos.
