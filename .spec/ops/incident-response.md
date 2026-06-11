# Runbook: Resposta a Incidente

> Trilha ops · e_seller · 2026-06-06 · Status: **Rascunho**

---

## Tipos de incidente prioritários

| Incidente | Sintoma | Ação imediata |
|---|---|---|
| Webhook falhando | pedidos pagos não viram `paid` | checar logs/alerta de webhook; o MP reenvia (idempotente) |
| Download negado em massa | clientes não baixam | checar grants/expiração/volume `ebook_files` |
| Pagamento com erro | checkout falha | checar credenciais MP / status do provedor |
| Vazamento de arquivo | e-book público | revogar acesso, checar `file_protection`, girar tokens |
| Indisponibilidade | API fora | checar healthcheck/db/containers |

## Fluxo geral

1. **Detectar** (alerta — ver [`../observability/alerting.md`](../observability/alerting.md)).
2. **Conter** (mitigar impacto imediato).
3. **Diagnosticar** (logs/métricas/tracing).
4. **Corrigir** (fix + verificação).
5. **Comunicar** (se afetar clientes/dados — LGPD pode exigir notificação).
6. **Post-mortem** (causa raiz + ação preventiva; vira teste/risco).

## Princípios

- Idempotência do webhook ajuda: reprocessar é seguro.
- Nunca expor dados pessoais nos canais de incidente.
- Toda correção emergencial vira **teste de regressão** (TDD) depois.

## Pendências

- [ ] Canal de alerta e on-call (mesmo simples).
- [ ] Template de post-mortem.
