# unit/security/

Units de segurança transversais, derivadas de
[`../../planning/19-seguranca-e-lgpd.md`](../../planning/19-seguranca-e-lgpd.md),
[`18`](../../planning/18-pagamentos-mercado-pago.md) e
[`20`](../../planning/20-entrega-ebook-anti-pirataria.md).

> ✅ **Todas as units deste índice foram geradas (2026-06-06).**

- ⬜ `jwt_tokens.md` — gerar/validar JWT (expiração, claims) (ADR-007).
- ⬜ `password_hashing.md` — hash/verify de senha (bcrypt/argon2).
- ⬜ `auth_dependency.md` — dependency FastAPI que exige `Bearer` válido.
- ⬜ `webhook_signature.md` — validar autenticidade do webhook Mercado Pago (RNF-02).
- ⬜ `download_token.md` — gerar token seguro com `secrets` (RF-30).
- ⬜ `file_protection.md` — garantir que arquivos de e-book não são servidos publicamente (RNF-03).
- ⬜ `cors.md` — política de CORS por ambiente (origens permitidas).
- ⬜ `secrets_management.md` — segredos só via env; nada no repo (RNF-04).
- ⬜ `lgpd_data_handling.md` — minimização, retenção e exclusão de dados pessoais (RNF-05,06).

> Estas units são **consumidas** pelas units de `backend/` (ex.: `accounts`, `payments`, `delivery`).
