# 04 — Requisitos Não-Funcionais (RNF)

> Documento de planning · e_seller · 2026-06-06
> Qualidades e restrições do sistema (o "como bem", não o "o quê").

---

## Convenção

`RNF-XX` — identificador estável. Cada RNF deve ser **verificável** (ter como medir).

---

## Segurança

| ID | Requisito | Como verificar |
|---|---|---|
| RNF-01 | Download liberado **apenas** após pagamento confirmado por webhook válido. | Teste: forçar "retorno" sem webhook não libera arquivo. |
| RNF-02 | Webhook do Mercado Pago deve validar autenticidade/assinatura. | Teste: payload sem assinatura válida é rejeitado. |
| RNF-03 | Arquivo do e-book nunca acessível por URL pública direta. | Teste: acesso ao path de storage retorna 403/404. |
| RNF-04 | Segredos (tokens, chaves) só via variáveis de ambiente, nunca no repo. | Revisão + `.env` no `.gitignore`. |

## Privacidade / LGPD

| ID | Requisito | Como verificar |
|---|---|---|
| RNF-05 | Coletar o mínimo de dados pessoais (e-mail para entrega). | Revisão do modelo de dados. |
| RNF-06 | Permitir exclusão de dados pessoais sob solicitação. | Procedimento documentado em [`19-seguranca-e-lgpd.md`](19-seguranca-e-lgpd.md). |

## Desempenho

| ID | Requisito | Meta |
|---|---|---|
| RNF-10 | Tempo de resposta das páginas de catálogo. | p95 < 500 ms em ambiente local. |
| RNF-11 | Processamento do webhook responde rápido e idempotente. | Resposta < 1 s; reentrega não duplica efeito. |

## Confiabilidade

| ID | Requisito | Meta |
|---|---|---|
| RNF-20 | Webhook idempotente (reentregas não criam efeitos duplicados). | Teste com webhook repetido. |
| RNF-21 | Falha de pagamento não corrompe o pedido (estados consistentes). | Máquina de estados testada. |

## Manutenibilidade

| ID | Requisito | Como verificar |
|---|---|---|
| RNF-30 | Código Python segue PEP 8, validado por Ruff. | CI falha se Ruff acusar erro. |
| RNF-31 | Cobertura de testes nas regras de negócio críticas. | Relatório de cobertura no CI. |
| RNF-32 | Toda funcionalidade nasce de uma spec (SDD). | Revisão de PR exige spec vinculada. |

## Portabilidade / Operação

| ID | Requisito | Como verificar |
|---|---|---|
| RNF-40 | Todo serviço (front, back, db) roda em **Docker**. | `docker compose up` sobe o ambiente completo. |
| RNF-41 | Ambiente reproduzível: Python 3.14.5+ fixado. | Imagem base e lockfile versionados. |
| RNF-42 | **Custo inicial zero**: sem dependência de serviços pagos para subir o projeto. | Revisão de dependências. |

## Acessibilidade & Compatibilidade

| ID | Requisito | Meta |
|---|---|---|
| RNF-50 | Páginas públicas responsivas (desktop/mobile). | Verificação manual em larguras comuns. |
| RNF-51 | Suporte aos navegadores modernos atuais. | Smoke test manual. |
