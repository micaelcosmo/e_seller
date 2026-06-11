# Runbook: Rotação de Segredos

> Trilha ops · e_seller · 2026-06-06 · Status: **Rascunho**

---

## Segredos do sistema

| Segredo | Impacto da rotação |
|---|---|
| `APP_SECRET_KEY` (JWT) | Invalida tokens existentes (re-login). |
| `MP_ACCESS_TOKEN` | Comunicação com Mercado Pago. |
| `MP_WEBHOOK_SECRET` | Validação de assinatura do webhook. |
| `POSTGRES_PASSWORD` | Acesso ao banco. |

## Procedimento geral

1. Gerar novo segredo no provedor/cofre.
2. Atualizar no cofre/secret manager (nunca em `.env` versionado — RNF-04).
3. Reimplantar/reiniciar o serviço para carregar o novo valor.
4. Verificar funcionamento (login, webhook, conexão DB).
5. Revogar o segredo antigo.

## Cuidados específicos

- **JWT (`APP_SECRET_KEY`):** rotacionar desloga todos; comunicar/planejar.
- **`MP_WEBHOOK_SECRET`:** alinhar com a configuração no painel do Mercado Pago.
- **DB:** atualizar `DATABASE_URL` e a senha do usuário no Postgres juntos.

## Verificação

- [ ] Login admin funciona.
- [ ] Webhook sandbox valida assinatura.
- [ ] Conexão ao banco OK.

## Pendências

- [ ] Cofre de segredos escolhido (provedor).
- [ ] Periodicidade de rotação.
