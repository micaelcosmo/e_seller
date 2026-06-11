# Convenções da API

> Trilha API · e_seller · 2026-06-06

---

## 1. Versionamento

- Prefixo **`/api/v1`** desde o início (evita quebra futura).
- Mudança incompatível → `/api/v2`; compatível → mesma versão.

## 2. Formato de erro

Padrão do FastAPI, consistente:
```json
{ "detail": "mensagem legível" }
```
- Validação (Pydantic) → `422` com lista de erros por campo.
- Erros de negócio → código adequado + `detail` **genérico** (não vazar internals).

## 3. Paginação

- Query: `limit` (default 20, máx 100) e `offset` (default 0).
- (A decidir) envelope com total vs lista pura — ver [`endpoints.md`](endpoints.md).

## 4. Autenticação

- `Authorization: Bearer <jwt>` nas rotas protegidas (ver [`../unit/security/auth_dependency.md`](../unit/security/auth_dependency.md)).
- Token obtido em `POST /api/v1/auth/token` (OAuth2 password).

## 5. CORS

- Origens permitidas por ambiente (`APP_ALLOWED_ORIGINS`); restrito em produção.
- Ver [`../unit/security/cors.md`](../unit/security/cors.md).

## 6. Convenções gerais

- Recursos por `slug`/`reference` (UUID), nunca `id` sequencial.
- Datas em ISO-8601 (UTC).
- Valores monetários como string decimal (`"39.90"`) para precisão.
- Nomes de campos em `snake_case`.

## 7. Idempotência

- Webhook do Mercado Pago é idempotente (ver [`errors.md`](errors.md) e
  [`../unit/backend/payments/service_process_webhook.md`](../unit/backend/payments/service_process_webhook.md)).
