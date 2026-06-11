# Unit: .env.example (`infra`)

> Tipo: `infra` · Área: `infra`
> Deriva de: [`planning/12`](../../planning/12-docker-e-ambientes.md) §5 · RNF-04 ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Documentar o contrato de variáveis de ambiente, **sem** valores reais.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/.env.example` |
| Teste | `backend/tests/infra/test_env_contract.py` (opcional) |

## 3. Conteúdo (contrato)

```
APP_ENV=dev
APP_SECRET_KEY=
APP_ALLOWED_ORIGINS=http://localhost:48173

# Portas (não-padrão — ver infra/ports.md)
BACKEND_PORT=48080
POSTGRES_PORT=48432
FRONTEND_PORT=48173
DASHBOARD_PORT=48088

# Banco PostgreSQL com driver ASYNC (asyncpg). Porta interna 5432; host = POSTGRES_PORT
DATABASE_URL=postgresql+asyncpg://e_seller:...@db:5432/e_seller
POSTGRES_DB=e_seller
POSTGRES_USER=e_seller
POSTGRES_PASSWORD=

MP_ACCESS_TOKEN=
MP_WEBHOOK_SECRET=
MP_ENVIRONMENT=sandbox
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/config.Settings` | as chaves devem casar com o Settings |
| `security/secrets_management` | política |

## 5. Comportamento / regras

- Mantido em sincronia com `Settings` (toda nova var aparece aqui sem valor).
- `.env` real fica fora do Git.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | Chaves do `.env.example` | cobrem todas as do `Settings` |
| T2 | Sem valores reais | apenas placeholders |

## 7. Rastreabilidade

- RNF-04 · Units: `core/config`, `security/secrets_management`, `docker_compose`

## 8. Pendências

- [ ] Variáveis específicas do frontend (quando existir).
