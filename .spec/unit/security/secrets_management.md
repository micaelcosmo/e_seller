# Unit: secrets_management (`security`/política)

> Tipo: `security` (política) · Área: `security`
> Deriva de: RNF-04 · [`planning/19`](../../planning/19-seguranca-e-lgpd.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Garantir que segredos nunca entrem no repositório e sejam carregados só por ambiente.

## 2. Localização

| Item | Caminho |
|---|---|
| Política | este doc + `core/config` + `.gitignore` |
| Teste | `backend/tests/security/test_secrets.py` |

## 3. Regras (contrato)

- Segredos só via env: `APP_SECRET_KEY`, `MP_ACCESS_TOKEN`, `MP_WEBHOOK_SECRET`, `POSTGRES_PASSWORD`.
- `.env` está no `.gitignore`; `.env.example` documenta as chaves **sem valores**.
- Em produção, segredos vêm de cofre/secret manager (não `.env`).

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/config` | leitura via env |
| `infra/env_config` | contrato do `.env.example` |

## 5. Comportamento / regras

- Nenhum segredo hardcoded no código (RNF-04).
- Scanner de segredos no CI/pre-commit (ver [`infra/ci_pipeline`](../infra/README.md)).

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | `.env` ignorado pelo Git | confirmado |
| T2 | App sem segredo obrigatório | falha clara na inicialização |
| T3 | grep por segredos no repo | nada encontrado |

## 7. Rastreabilidade

- RNF-04 · Planning [`19`](../../planning/19-seguranca-e-lgpd.md) · Units: `core/config`, `infra/env_config`

## 8. Pendências

- [ ] Ferramenta de scan de segredos (ex.: `gitleaks`).
