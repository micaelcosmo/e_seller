# .spec/observability/

Trilha **viva** de observabilidade: logs, métricas, alertas e tracing — para sabermos
se o sistema está saudável e diagnosticar incidentes ([`../ops/incident-response.md`](../ops/incident-response.md)).

## Documentos

| Doc | Assunto |
|---|---|
| [`logging.md`](logging.md) | Logging estruturado; o que (não) logar. |
| [`metrics.md`](metrics.md) | Métricas-chave de negócio e técnicas. |
| [`alerting.md`](alerting.md) | Alertas e limiares. |
| [`tracing.md`](tracing.md) | Correlação/tracing de requisições. |

## Princípios

- **Custo zero inicial:** começar com logs estruturados + métricas simples
  (open-source); evoluir conforme necessidade.
- **Sem dados pessoais/segredos** em logs/métricas (LGPD/RNF-04).

## Regra de manutenção

Atualizar a cada nova métrica/alerta/log relevante e registrar em [`CHANGELOG.md`](CHANGELOG.md).
