# Unit: Settings (`config`)

> Tipo: `config` · Área: `backend/core`
> Deriva de: [`planning/12`](../../../planning/12-docker-e-ambientes.md) · RNF-04, RNF-41 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Carregar configuração da aplicação a partir de **variáveis de ambiente** (12-factor),
sem nenhum segredo no código e sem variáveis globais soltas.

## 2. Localização (proposta)

| Item | Caminho |
|---|---|
| Código | `backend/app/core/config.py::Settings` |
| Teste | `backend/tests/core/test_config.py` |

## 3. Contrato (assinatura)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_env: str = "dev"
    app_secret_key: str
    app_allowed_origins: str = ""
    database_url: str
    mp_access_token: str = ""
    mp_webhook_secret: str = ""
    mp_environment: str = "sandbox"


def get_settings() -> Settings:
    ...  # instância única (cache), injetada via Depends — não é global mutável
```

- **Saída:** instância de `Settings` validada.
- **Erros:** erro de validação Pydantic se faltar variável obrigatória (`app_secret_key`, `database_url`).

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `pydantic-settings` | Ler/validar env | real |
| variáveis de ambiente / `.env` | Fonte de config | env de teste / `monkeypatch` |

## 5. Comportamento / regras

- Sem segredos no repositório; só via env (RNF-04).
- `get_settings()` é injetável (`Depends`), evitando estado global mutável (ver [`oop-and-naming`](../../../standards/oop-and-naming.md)).
- `app_allowed_origins` é parseado para lista (CORS) — ver [`security/cors`](../../security/README.md).

## 6. Casos de teste (TDD)

| # | Cenário | Entrada | Esperado |
|---|---|---|---|
| T1 | Variáveis completas | env válido | `Settings` carrega valores corretos |
| T2 | Falta `database_url` | env incompleto | erro de validação |
| T3 | Default de `app_env` | sem `APP_ENV` | `app_env == "dev"` |

## 7. Rastreabilidade

- RNF-04, RNF-41 · Planning [`12`](../../../planning/12-docker-e-ambientes.md)
- Units relacionadas: `core/db_session`, `security/cors`, `security/secrets_management`

## 8. Pendências

- [ ] Parsing de `app_allowed_origins` (CSV → lista) aqui ou no módulo de CORS.
