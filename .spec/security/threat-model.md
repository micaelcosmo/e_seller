# Threat Model (STRIDE)

> Trilha security · e_seller · 2026-06-10 · Status: **Atualizado**

---

## 1. Ativos a proteger

| Ativo | Por quê |
|---|---|
| Arquivos de e-book | É o produto; vazamento = prejuízo (anti-pirataria). |
| Pagamentos/pedidos | Integridade financeira; idempotência. |
| Dados pessoais (e-mail, CPF/CNPJ) | LGPD Art. 9 / Art. 18. |
| Credenciais/segredos | Acesso ao sistema/MP/DB/JWT. |
| Sessão admin | Controle do catálogo e dados. |
| Perfis fiscais (billing_profile) | Dados sensíveis (CPF/CNPJ, endereço). |

---

## 2. Superfícies de entrada

- API pública (catálogo, criar pedido, download, newsletter).
- Webhook do Mercado Pago (entrada de terceiro autenticada por HMAC).
- Painel admin (SQLAdmin) + login de staff/admin.
- Upload de arquivos de e-book (admin, multipart).
- Importação de manifest via URL (modo link — anti-SSRF implementado).
- Endpoint de exclusão LGPD (`DELETE /auth/account`).

---

## 3. STRIDE — ameaças e mitigações

| Categoria | Ameaça | Mitigação | Implementado |
|---|---|---|---|
| **S**poofing | Webhook forjado | HMAC-SHA256 (`x-signature`); `WebhookSignatureValidator` | ✅ PAY-02 |
| **S**poofing | Acesso sem login | JWT + `RequireRole`; rate limit no login | ✅ AUTH-01/SEC-01 |
| **T**ampering | Adulterar JWT | Assinatura HS256 verificada; expiração | ✅ AUTH-01 |
| **T**ampering | Forçar `paid` sem pagar | Estado só muda por webhook válido (idempotente) | ✅ PAY-02 |
| **T**ampering | Cupom inválido/negativo | CouponService impede desconto negativo; limites | ✅ DOM-04 |
| **T**ampering | Upload malicioso | Extensão validada; tamanho máximo 50 MB; ProtectedStorage | ✅ PROD-05 |
| **T**ampering | SSRF via modo link | Validação de host (localhost/privado bloqueado) | ✅ PROD-04 |
| **R**epudiation | Negar download/compra | `download_log` (auditoria por hash de IP + grant) | ✅ DOM-02 |
| **R**epudiation | Ação admin sem rastro | Correlation ID em todos os logs JSON | ✅ OPS-01 |
| **I**nfo disclosure | Vazar arquivo de e-book | Volume protegido + token + anti path traversal | ✅ PROD-05/SEC-01 |
| **I**nfo disclosure | Vazar dados pessoais | Anonimização LGPD (hash SHA-256); billingProfile read-only | ✅ SEC-02/DOM-10 |
| **I**nfo disclosure | Vazar segredos no log | LoggingConfig sem PII; gitleaks no CI | ✅ CI-03 |
| **I**nfo disclosure | CORS irrestrito em prod | `CORS_ORIGINS` configurável por env | ✅ SEC-06 |
| **D**oS | Flood de download | Limite por grant (`download_max`) + expiração | ✅ DOM-01/SEC-01 |
| **D**oS | Flood de login/webhook | Rate limit in-memory (janela deslizante por IP) | ✅ SEC-01 |
| **D**oS | Grant inválido pós-estorno | `GrantRevoker` expira grants no estorno | ✅ DOM-12 |
| **E**lev. privilégio | Não-admin acessa painel | `RequireRole("admin","staff")`; RBAC em todos endpoints | ✅ AUTH-02/ADM-02 |
| **E**lev. privilégio | Review sem compra | Verificação de entitlement antes de permitir review | ✅ DOM-03 |
| **E**lev. privilégio | Customer acessa admin | RBAC verifica papel em todos endpoints admin | ✅ AUTH-02 |

---

## 4. Riscos residuais

| Risco | Status | Tier |
|---|---|---|
| **Watermark** por comprador (anti-pirataria avançada) | Não implementado | 🟡 Tier 2 |
| **2FA/MFA** para admin | Não implementado | 🟡 Tier 2 |
| **Mercado Pago real** (webhook prod) | Depende de conta MP | 🔴 PAY-01 |
| **Auditoria de billing_profile** (dado sensível) | Leitura no admin protegida; sem trilha de mudança | 🟡 Tier 2 |

---

## 5. Relacionado

Planning [`19`](../planning/19-seguranca-e-lgpd.md),
[`20`](../planning/20-entrega-ebook-anti-pirataria.md) ·
testes [`../unit/tests/security_testing.md`](../unit/tests/security_testing.md) ·
riscos [`../planning/22-matriz-de-riscos.md`](../planning/22-matriz-de-riscos.md).

---

## 6. Changelog

- **2026-06-10**: Atualizado com novos domínios (cupons, reviews, wishlist, billing, refund,
  newsletter, upload, SSRF, estorno). Rate limit, CORS, LGPD e HMAC marcados como implementados.
