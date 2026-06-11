# 19 — Segurança e LGPD

> Documento de planning · e_seller · 2026-06-06
> Proteção da aplicação e dos dados pessoais (Lei Geral de Proteção de Dados).

---

## 1. Dados pessoais tratados

| Dado | Finalidade | Base legal (LGPD) |
|---|---|---|
| E-mail do comprador | Identificar pedido e entregar o e-book | Execução de contrato |
| Dados de pagamento | Processados pelo **Mercado Pago** (não armazenamos cartão) | Execução de contrato |
| `raw_payload` do pagamento | Auditoria/conciliação | Legítimo interesse / obrigação |

> 💡 **Não armazenamos dados de cartão.** Eles ficam com o Mercado Pago, que é o
> responsável por PCI-DSS. Reduz drasticamente nosso risco.

## 2. Princípios LGPD aplicados

- **Minimização:** coletar só o necessário (e-mail) — RNF-05.
- **Finalidade:** usar os dados só para o que foi informado.
- **Transparência:** política de privacidade clara no portal.
- **Direitos do titular:** permitir acesso/exclusão sob solicitação (RNF-06).
- **Retenção:** definir prazo para descartar `raw_payload`/pedidos antigos.

## 3. Direitos do titular — procedimento (proposta)

- Canal de contato (e-mail/formulário) para solicitações.
- Exclusão: anonimizar `buyer_email` e remover payloads após confirmação,
  preservando o mínimo exigido por lei fiscal/contábil.
- Prazo de resposta conforme a LGPD.

## 4. Segurança da aplicação (checklist)

| Tema | Medida |
|---|---|
| Segredos | Só via env vars; `.env` no `.gitignore` (RNF-04). |
| HTTPS | Obrigatório em produção (cookies seguros, HSTS). |
| Config de app | `APP_ENV=prod`, `/docs` restrito/desligado em prod, `APP_SECRET_KEY` forte. |
| CORS | Restringir `APP_ALLOWED_ORIGINS` ao domínio do frontend (serviços separados). |
| Auth | JWT com expiração curta; hash de senha forte (ex.: bcrypt/argon2) — ADR-007. |
| Injeção | ORM **SQLAlchemy** (queries parametrizadas) — evitar SQL cru. |
| Validação | **Pydantic** valida toda entrada da API por padrão. |
| XSS | Responsabilidade principalmente do frontend; API retorna JSON, não HTML. |
| Upload | Validar tipo/tamanho do arquivo de e-book (RF-12). |
| Webhook | Validar assinatura + idempotência (RNF-02, RNF-20). |
| Download | Token secreto, expiração, limite, arquivo não público (RNF-03). |
| Dependências | Atualizar e checar vulnerabilidades (ex.: `pip-audit`, gratuito). |

## 5. Segredos e configuração

- `DJANGO_SECRET_KEY`, `MP_ACCESS_TOKEN`, `MP_WEBHOOK_SECRET`, credenciais do DB.
- Dev: `.env` local (ignorado). Prod: cofre/secret manager do destino de deploy.
- `.env.example` documenta as chaves **sem valores reais**.

## 6. Logs e auditoria

- Logar eventos sensíveis (mudança de status de pedido, downloads) **sem** vazar dados pessoais em texto.
- Não logar tokens nem payloads completos em produção.

## 7. Backups

- Backup do PostgreSQL (mesmo simples no início) — proteger contra perda.
- Backups também sujeitos à LGPD (retenção/segurança).

## 8. Pendências

- [ ] Redigir política de privacidade e termos de uso.
- [ ] Definir prazos de retenção (pedidos, payloads, logs).
- [ ] Definir cofre de segredos do ambiente de produção.
