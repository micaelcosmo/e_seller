# 22 — Matriz de Riscos

> Documento de planning · e_seller · 2026-06-06
> Riscos do projeto, impacto, probabilidade e mitigação.

---

## Escala

- **Impacto:** Baixo / Médio / Alto
- **Probabilidade:** Baixa / Média / Alta
- **Prioridade** = combinação (Alto+Alta = crítico 🔴).

---

## Riscos técnicos

| ID | Risco | Impacto | Prob. | Mitigação |
|---|---|---|---|---|
| R-01 | Stack (FastAPI/SQLAlchemy/Pydantic) incompatível com Python 3.14.5+ | Alto | Baixa | Confirmar/fixar versões no M0; CI na 3.14. Risco menor que com Django. Ver [`07`](07-adr-stack.md). |
| R-02 | Webhook não idempotente → entregas/efeitos duplicados | Alto | Média | `provider_payment_id` único + testes de duplicidade (RNF-20). |
| R-03 | Download liberado sem pagamento real | Alto | Baixa | Liberar só por webhook validado; testes de retorno-sem-webhook (RNF-01). |
| R-04 | Vazamento de arquivo de e-book | Alto | Média | Arquivo não público + token/expiração/limite + marca d'água futura ([`20`](20-entrega-ebook-anti-pirataria.md)). |
| R-05 | Segredos commitados | Alto | Baixa | `.env` ignorado, revisão de PR, pre-commit, scanner de segredos. |
| R-06 | Mudança no payload/assinatura do Mercado Pago | Médio | Média | Cliente isolado/mockável; validar contra sandbox; testes de contrato. |
| R-07 | Auth/admin "na mão" (sem Django) introduzir falha de segurança | Alto | Média | Usar libs maduras (fastapi-users/SQLAdmin), JWT com expiração, hash forte; testes de autorização. Ver ADR-007/008. |
| R-08 | Mais setup inicial (ORM/migrations/auth) atrasar o M0/M1 | Médio | Média | Marcos pequenos; reaproveitar libs prontas; não reinventar. |

## Riscos de produto/escopo

| ID | Risco | Impacto | Prob. | Mitigação |
|---|---|---|---|---|
| R-10 | Escopo do MVP crescer (scope creep) | Médio | Alta | MoSCoW + escopo fechado em [`06`](06-escopo-mvp.md); novidades viram pós-MVP. |
| R-11 | Decisão de frontend bloquear backend | Médio | Baixa | Backend é API JSON independente + SQLAdmin; serviços separados; decisão adiada sem travar (ADR-005). |
| R-12 | Requisito legal (NF, LGPD) subestimado | Médio | Média | Tratar cedo em [`19`](19-seguranca-e-lgpd.md); minimizar dados. |

## Riscos operacionais

| ID | Risco | Impacto | Prob. | Mitigação |
|---|---|---|---|---|
| R-20 | Custo de infra surgir (contra "custo zero") | Médio | Média | Stack 100% open-source; hospedagem definida no roadmap com foco em custo baixo. |
| R-21 | Perda de dados (sem backup) | Alto | Baixa | Backups do Postgres desde cedo ([`19`](19-seguranca-e-lgpd.md) §7). |
| R-22 | Falta de prática em FastAPI/SQLAlchemy atrasar entregas | Médio | Média | Documentos didáticos; marcos pequenos e incrementais ([`21`](21-roadmap.md)). |

## Riscos de processo

| ID | Risco | Impacto | Prob. | Mitigação |
|---|---|---|---|---|
| R-30 | Spec e código divergirem | Médio | Média | SDD: spec no mesmo PR; revisão exige spec ([`17`](17-fluxo-sdd.md)). |
| R-31 | Testes pulados "porque é simples" | Médio | Média | TDD obrigatório na DoD ([`16`](16-definition-of-done.md)); gate de cobertura no CI. |

---

## Top 3 a vigiar

1. **R-02 / R-03** — integridade do pagamento↔entrega (núcleo do negócio).
2. **R-07** — segurança de auth/admin (agora sob nossa responsabilidade, sem Django).
3. **R-04** — vazamento do produto digital.

## Pendências

- [ ] Reavaliar a matriz ao fim do M0 (quando a stack estiver materializada).
