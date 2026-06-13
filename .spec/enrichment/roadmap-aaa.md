# Planning AAA — Authentication, Authorization, Accounting

> Enrichment de segurança para o e_seller. Cada feature aqui é justificada por lacuna
> real no MVP — não especulação. Última atualização: 2026-06-13.

---

## 1. Token Blacklist (Revogação de JWT)

**Problema:** logout hoje não invalida o token. Um token roubado permanece válido até expirar (1h).

**Solução:** tabela `RevokedToken` com `jti` (JWT ID claim) + `expires_at`. Ao fazer logout,
o `jti` é inserido. `get_current_user` verifica blacklist antes de autorizar.

**Modelo:**
```
RevokedToken
  id: int PK
  jti: str UNIQUE INDEX
  expires_at: datetime TZ
  revoked_at: datetime TZ default now
```

**Endpoints:**
- `POST /api/v1/auth/logout` — revoga token atual; retorna 204.

**Serviço:** `TokenBlacklistService(session)` com métodos `revoke(jti, expires_at)` e `is_revoked(jti)`.

**Impacto em `get_current_user`:** após verificar assinatura, checar blacklist. Se revogado → 401.

**JTI:** adicionar claim `jti` (UUID4) ao `JwtService.issue()`. Verificar e extrair em `deps.py`.

---

## 2. User Activity Log (Accounting)

**Problema:** só `LoginAttempt` existe; compras, downloads e edições de perfil não são auditados.

**Solução:** `UserActivityLog` genérico com `event_type` + `metadata` JSON.

**Modelo:**
```
UserActivityLog
  id: int PK
  user_id: int FK User (nullable para anônimos)
  event_type: str INDEX ("login", "purchase", "download", "profile_update", "2fa_enrolled")
  metadata: JSON (coupon_code, product_id, ip, etc.)
  created_at: datetime TZ INDEX
```

**Serviço:** `UserActivityLogService(session)` com método `log(user_id, event_type, **meta)`.

**Integração:** injetar nos services de accounts, orders, delivery, accounts.

**Endpoint:** `GET /api/v1/me/activity?limit=20` — lista atividades do usuário autenticado.

---

## 3. API Keys (Autenticação Programática)

**Problema:** não há forma de autenticar sem sessão interativa (ex.: scripts, webhooks externos).

**Solução:** chaves de API geradas com `secrets.token_urlsafe(32)`, hash SHA-256 armazenado.
Autenticação via header `X-API-Key`.

**Modelo:**
```
ApiKey
  id: int PK
  user_id: int FK User
  name: str (label do usuário)
  key_hash: str UNIQUE INDEX (SHA-256 da chave)
  prefix: str (8 chars iniciais; exibido na listagem)
  is_active: bool default True
  last_used_at: datetime TZ nullable
  expires_at: datetime TZ nullable
  created_at: datetime TZ
```

**Serviço:** `ApiKeyService(session)` com:
- `generate(user_id, name, expires_at)` → retorna chave crua (exibida 1 vez)
- `authenticate(raw_key)` → User ou None
- `revoke(key_id, user_id)`
- `list_keys(user_id)`

**Endpoints:**
- `GET /api/v1/me/api-keys` — lista chaves (sem revelar o hash)
- `POST /api/v1/me/api-keys` — cria nova chave
- `DELETE /api/v1/me/api-keys/{id}` — revoga chave

**Dependency:** `authenticate_api_key` — extrai `X-API-Key`, valida hash, retorna User.

---

## 4. 2FA / TOTP (Two-Factor Authentication)

**Problema:** admin e staff podem ser comprometidos por credential stuffing.
2FA elimina o vetor de senhas vazadas.

**Solução:** TOTP (RFC 6238) via `pyotp`. Secret por usuário (AES-encrypted via settings key).
Enforcement progressivo: staff/admin obrigados; customer opcional.

**Coluna adicionada a `User`:**
```
totp_secret_enc: str nullable  — secret cifrado em AES-GCM (base64)
totp_enabled: bool default False
```

**Serviço:** `TOTPService(settings)` com:
- `generate_secret()` → str base32
- `generate_provisioning_uri(secret, email)` → str (para QR code)
- `verify(secret, code, window=1)` → bool
- `encrypt_secret(secret)` / `decrypt_secret(enc)` — AES-GCM via settings.totp_encryption_key

**Fluxo de enrollment:**
1. `POST /api/v1/auth/2fa/enroll` — gera secret + URI (user não tem 2FA)
2. User configura app (Authenticator), digita código
3. `POST /api/v1/auth/2fa/confirm` — valida código, persiste `totp_secret_enc + totp_enabled=True`

**Fluxo de login com 2FA:**
1. `POST /api/v1/auth/token` — credenciais OK → retorna `partial_token` se 2FA habilitado
2. `POST /api/v1/auth/2fa/login` — partial_token + código TOTP → tokens completos

**Disable:**
- `POST /api/v1/auth/2fa/disable` — exige senha atual + código TOTP correto

**Settings novas:**
```
totp_encryption_key: str  — chave AES-GCM base64 (32 bytes)
two_fa_required_roles: list[str] = ["admin", "staff"]  — papéis que precisam de 2FA
```

---

## 5. Per-User Rate Limiting

**Problema:** rate limit atual é por IP. Múltiplos usuários em NAT partilham limite;
usuário autenticado não tem limite individual.

**Solução:** no `Depends(get_current_user)`, aplicar sliding window por `user.id`.
Limite distinto de anônimos (por IP).

**Config:** `Settings.rate_limit_authed_rpm: int = 120` (rpm = requests per minute).

---

## 6. Ownership Checks Reforçados

**Problema:** `GET /api/v1/orders/{id}` valida apenas autenticação, não propriedade.
Usuário poderia inferir IDs e acessar pedidos alheios.

**Solução:** adicionar `WHERE order.user_id = current_user.id` (ou `buyer_email = current_user.email`)
em todos endpoints de leitura de pedido, download, entitlement do contexto `/me/*`.
Endpoints admin (`RequireRole("admin","staff")`) permanecem irrestri​tos.

---

## Ordem de implementação (TDD)

```
RevokedToken model + migration
→ TokenBlacklistService
→ JwtService.issue() adiciona jti
→ get_current_user verifica blacklist
→ POST /auth/logout
→ Testes (3+)
→ UserActivityLog model + migration
→ UserActivityLogService
→ Integração nos services
→ GET /me/activity
→ Testes (3+)
→ ApiKey model + migration
→ ApiKeyService
→ Endpoints /me/api-keys
→ Dependency authenticate_api_key
→ Testes (3+)
→ User.totp_secret_enc + totp_enabled migration
→ TOTPService
→ Endpoints 2fa/enroll, confirm, disable, login
→ Testes (3+)
→ Per-user rate limit
→ Ownership checks
→ Revisão cíclica
```

---

## Definition of Done

- [ ] Testes verdes (3+ por feature)
- [ ] Ruff limpo
- [ ] Nenhum segredo em hardcode
- [ ] Models documentados no UML
- [ ] Migration Alembic gerada
- [ ] Spec YAML adversarial validada
