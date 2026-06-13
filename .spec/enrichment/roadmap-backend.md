# Planning Backend Enrichment (BEE)

> Features de backend que aumentam qualidade e engajamento sem sair do contexto
> "vender e-books". Última atualização: 2026-06-13.

---

## 1. Email Service (Transacional Pluggável)

**Problema:** sem e-mail, usuário não recebe confirmação de compra, link de download
ou recuperação de senha. Engajamento zero pós-compra.

**Decisão:** `EmailService` pluggável. Se `SMTP_HOST` não definido → modo "log only"
(imprime o e-mail no log, não falha). Integração opcional, zero-custo em dev.

**Serviço:** `EmailService(settings)` com:
- `send(to, subject, html_body)` → async
- `send_order_paid(email, order_ref, download_links)` 
- `send_password_reset(email, reset_link)`
- `send_download_expiring(email, product_title, grant_expires_at)`

**Templates:** `backend/app/core/email_templates/` — HTML simples, inline CSS, sem framework.

**Settings:**
```
smtp_host: str = ""
smtp_port: int = 587
smtp_user: str = ""
smtp_password: str = ""
smtp_from: str = "noreply@e-seller.local"
smtp_use_tls: bool = True
```

**Integração:** após `OrderService.process_paid()`, chamar `EmailService.send_order_paid()`.
Após `Authenticator.reset_password()`, chamar `EmailService.send_password_reset()`.

---

## 2. Endpoints /me/* (Perfil Unificado)

**Problema:** não há endpoint único para o usuário ver seus dados. Cada domínio tem
endpoints separados que exigem que o frontend faça múltiplas chamadas.

**Solução:** endpoints `GET /api/v1/me/*` que encapsulam dados do usuário autenticado.

| Endpoint | Dados retornados |
|---|---|
| `GET /api/v1/me` | perfil: email, role, billing_profile |
| `GET /api/v1/me/orders` | lista de pedidos do usuário |
| `GET /api/v1/me/library` | entitlements + grants ativos |
| `GET /api/v1/me/wishlist` | itens da wishlist |
| `GET /api/v1/me/cart` | itens do carrinho |
| `GET /api/v1/me/activity` | user_activity_logs (AAA) |
| `GET /api/v1/me/api-keys` | API keys (AAA) |

**Implementação:** router `router_me.py` em `accounts/`; delega para services existentes.
Todos protegidos por `Depends(get_current_user)`.

---

## 3. Health Check Enrichment

**Problema:** `/healthz` retorna apenas `{"status":"ok"}`. Não expõe latência do DB,
uso de disco ou checks de dependências.

**Solução:**
```json
{
  "status": "ok",
  "db_latency_ms": 4.2,
  "disk_free_mb": 12304,
  "version": "1.0.0-enrichment",
  "checks": {
    "database": "ok",
    "disk": "ok"
  }
}
```

**Serviço:** `HealthService(session, settings)` com método `collect()`.
Timeout de 2s no check de DB; se falhar → `"database": "degraded"`, HTTP 503.

---

## 4. Problem+JSON (RFC 9457) em Erros

**Problema:** erros retornam `{"detail": "mensagem"}` (padrão FastAPI). Não há `type`,
`title` ou `instance`. Dificulta diagnóstico programático.

**Solução:** `exception_handlers.py` adiciona campos RFC 9457:
```json
{
  "type": "urn:eseller:error:not_found",
  "title": "Não encontrado",
  "status": 404,
  "detail": "Produto não encontrado",
  "instance": "/api/v1/products/slug-invalido"
}
```

Headers: `Content-Type: application/problem+json`.

**Impacto:** backward-compatible (campo `detail` mantido). Frontend pode usar `type`
para i18n futura.

---

## 5. OpenAPI Enrichment

**Problema:** `/docs` tem endpoints sem tag, sem descrição, sem exemplos de resposta.
DX ruim para integração futura (Next.js, mobile, parceiros).

**Solução:**
- Adicionar `tags=["products"]`, `summary=`, `description=` em todos os routers
- `FastAPI(title=, description=, version=, contact=, license_info=)`
- `responses={200: {"content": {"application/json": {"example": {...}}}}}` em endpoints principais
- `operation_id` explícito nos endpoints de catálogo e auth

---

## Definition of Done

- [ ] `EmailService` com modo log-only e SMTP opcional
- [ ] Templates HTML para order_paid, password_reset, download_expiring
- [ ] Email disparado em OrderService.process_paid() e Authenticator.reset_password()
- [ ] Testes EmailService (mock SMTP, valida campos)
- [ ] GET /me + GET /me/orders + /library + /wishlist + /cart + /activity
- [ ] GET /me/api-keys (depende de AAA)
- [ ] Health enrichment: DB latency + disk + checks
- [ ] Problem+JSON em exception_handlers
- [ ] OpenAPI: tags, summaries, examples em endpoints principais
- [ ] Ruff limpo; testes verdes
