# Runbook: Exclusão de Dados (LGPD)

> Trilha ops · e_seller · 2026-06-06 · Status: **Rascunho**
> Implementa o direito do titular (RNF-06). Ver [`../planning/19-seguranca-e-lgpd.md`](../planning/19-seguranca-e-lgpd.md)
> e [`../unit/security/lgpd_data_handling.md`](../unit/security/lgpd_data_handling.md).

---

## Quando

Pedido de exclusão/anonimização de dados pessoais por um titular (comprador).

## Pré-requisitos

- Identificar o titular pelo `buyer_email`.
- Confirmar identidade do solicitante (evitar exclusão indevida).

## Passos

1. Localizar pedidos/pagamentos vinculados ao `buyer_email`.
2. Executar o procedimento de exclusão (`DataEraser.erase_buyer(email)`):
   - **Anonimizar** `buyer_email` nos pedidos.
   - **Remover** `payment.raw_payload` e dados pessoais em logs.
3. **Preservar o mínimo legal** (registros fiscais/contábeis obrigatórios) — não apagar o que a lei exige manter.
4. Registrar a operação em auditoria (sem vazar dados pessoais).
5. Responder ao titular dentro do prazo legal.

## Cuidados

- Backups também contêm dados pessoais → aplicar política de retenção/expiração.
- Não confundir exclusão com cancelamento de pedido.

## Verificação

- [ ] `buyer_email` anonimizado nos registros aplicáveis.
- [ ] Payloads/logs pessoais removidos.
- [ ] Mínimo legal preservado.

## Pendências

- [ ] Prazos de retenção concretos; texto de resposta padrão.
