# .spec/ops/

Trilha **viva** de operação (runbooks): procedimentos passo a passo para rodar o
e_seller em produção com segurança e baixo custo.

> Runbooks são para serem **executados sob pressão** — objetivos, com passos
> numerados, pré-requisitos e verificação.

## Runbooks

| Runbook | Quando usar |
|---|---|
| [`deploy.md`](deploy.md) | Publicar uma nova versão. |
| [`backup-restore.md`](backup-restore.md) | Backup e restauração do PostgreSQL. |
| [`secrets-rotation.md`](secrets-rotation.md) | Rotacionar segredos (JWT, MP, DB). |
| [`lgpd-data-deletion.md`](lgpd-data-deletion.md) | Atender pedido de exclusão de dados (LGPD). |
| [`incident-response.md`](incident-response.md) | Resposta a incidente (pagamento/entrega/segurança). |

## Regra de manutenção

Atualizar o runbook **sempre que o procedimento mudar** e registrar em
[`CHANGELOG.md`](CHANGELOG.md). Idealmente, validar cada runbook em um *drill*.

## Relacionado

Planning [`12`](../planning/12-docker-e-ambientes.md), [`15`](../planning/15-ci-cd.md),
[`19`](../planning/19-seguranca-e-lgpd.md) · trilha [`observability`](../observability/).
