# Unit: Database / get_session (`config`) — ASYNC

> Tipo: `config`/infra de dados · Área: `backend/core`
> Deriva de: ADR-002/003 ([`planning/07`](../../../planning/07-adr-stack.md)) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

> **Decisão (2026-06-07):** banco **PostgreSQL** **async**. Driver: **psycopg3**
> (`postgresql+psycopg://`) — escolhido em 2026-06-10 no lugar do asyncpg, que ainda
> não tem wheel para CPython 3.14. Sessão **assíncrona** (`AsyncSession`); services `async`.
> Dev/test usam `sqlite+aiosqlite`.

---

## 1. Objetivo

Criar o engine **assíncrono** (SQLAlchemy + asyncpg) e fornecer **sessões async por
request**, injetáveis nos services, sem estado global mutável.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/core/db.py` (`Base`, `Database`, `get_session`) |
| Teste | `backend/tests/core/test_db_session.py` |

## 3. Contrato

```python
class Database:
    def __init__(self, database_url: str) -> None:
        # ex.: postgresql+asyncpg://user:pass@db:5432/e_seller
        self.engine = create_async_engine(database_url, future=True)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    def create_session(self) -> AsyncSession:
        return self.session_factory()


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Dependency: entrega AsyncSession, faz commit no sucesso e fecha."""
    database: Database = request.app.state.database
    session = database.create_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
```

- **Saída:** `AsyncSession` por request; fechada ao final.
- **Erros:** propaga erro de conexão.

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `core/config.Settings.database_url` | URL `postgresql+asyncpg://...` | Postgres de teste |
| SQLAlchemy async + `asyncpg` | engine/sessão | real (DB de teste) |

## 5. Comportamento / regras

- `Database` encapsula engine/factory (POO; sem globais).
- `get_session` é **async**; garante commit/rollback/close.
- Migrations via **Alembic** (não `create_all` em produção).
- Em teste, usar Postgres efêmero (container) ou transação revertida por teste.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Criar sessão async | retorna `AsyncSession` utilizável |
| T2 | Encerramento | sessão é fechada após o uso |
| T3 | URL inválida | erro de conexão ao usar |

## 7. Rastreabilidade

- ADR-002/003 · Units: `core/config`, todos os `model_*`, `tests/conftest_db`

## 8. Pendências

- [ ] Fixar versão exata de `asyncpg` (validar em 3.14.5).
- [ ] Estratégia de DB de teste: Postgres em container vs `pytest` com transação.
- [ ] **Débito do MVP:** o código atual roda **sync + SQLite**; migrar para async + Postgres.
