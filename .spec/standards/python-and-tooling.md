# Python e Ferramentas

> Padrão · e_seller · 2026-06-07 (decisões fechadas)

---

## 1. Versão do Python

- **Python 3.14** — fixar sempre o **patch estável mais recente** da série 3.14
  (mínimo **3.14.5**, conforme decidido).
- Declarar em `pyproject.toml`: `requires-python = ">=3.14"`.
- A imagem Docker usa tag pinada (ex.: `python:3.14-slim`) — sem `latest`.
- CI roda exatamente na mesma versão (ver [`enforcement.md`](enforcement.md)).

## 1b. Versões fixadas (validadas rodando em Python 3.14.5)

> Estas versões foram **instaladas e testadas** (22 testes verdes) no MVP. Fixar no
> `pyproject.toml`/lockfile. Atualizar esta tabela ao subir versões.

| Pacote | Versão | Papel |
|---|---|---|
| fastapi | 0.136.3 | framework web |
| starlette | 1.2.1 | base ASGI (via fastapi) |
| pydantic | 2.13.4 | validação/schemas |
| pydantic-settings | 2.14.1 | config por env |
| sqlalchemy | 2.0.50 | ORM |
| uvicorn | 0.49.0 | servidor ASGI (dev) |
| anyio | 4.13.0 | runtime async |
| jinja2 | 3.1.6 | templates (vitrine demo) |
| python-multipart | 0.0.32 | forms |
| httpx | 0.28.1 | client de teste |
| pytest | 9.0.3 | testes |
| pytest-asyncio | (a fixar) | testes async |
| ruff | 0.15.16 | lint/format |
| **psycopg[binary]** | **3.2.x** | driver Postgres **async** (wheel cp314; leve, sem compilar) |
| aiosqlite | 0.21.0 | SQLite async (dev/test) |

> ✅ **Validado:** o backend roda async contra **PostgreSQL via psycopg3**
> (`postgresql+psycopg://`) em Docker. Trocamos `asyncpg` por `psycopg3` porque o
> asyncpg ainda **não** tem wheel para CPython 3.14 (exigia compilar com gcc).

## 2. Gerência de dependências — **uv** (decidido)

- **uv** é o gerenciador oficial: rápido, com **lockfile** (`uv.lock`) versionado para
  builds determinísticos. `pyproject.toml` como fonte das dependências.
- Dependências de desenvolvimento em grupo `dev` separado.
- Comandos típicos: `uv sync` (instala do lock), `uv add <pkg>`, `uv run pytest`.

> Nota: o MVP foi montado com `venv`+`pip` (rápido p/ subir no ar). Migrar para `uv`
> é um passo de implementação (gera `uv.lock`).

## 3. Qualidade de código

| Ferramenta | Papel |
|---|---|
| **Ruff** | Lint **e** formatação (PEP 8, imports). Única fonte de estilo automático. |
| **pytest** + **pytest-asyncio** | Testes (TDD). |
| **pytest-cov** | Cobertura. |
| **pre-commit** | Roda Ruff antes de cada commit. |

## 4. Config base do Ruff (`pyproject.toml`)

```toml
[tool.ruff]
line-length = 88
target-version = "py314"

[tool.ruff.lint]
# NÃO habilitar "C4" (flake8-comprehensions): ela INCENTIVA comprehensions,
# o que contraria nosso padrão de laços explícitos (ver oop-and-naming.md).
select = ["E", "F", "I", "B", "UP", "ASYNC", "N", "PL"]
# E/F: PEP8+pyflakes · I: imports · B: bugbear · UP: pyupgrade
# ASYNC: boas práticas async · N: pep8-naming · PL: pylint (parcial)

[tool.ruff.format]
quote-style = "double"
```

## 5. Type hints

- Usar **type hints** em métodos públicos, construtores e assinaturas de service.
- `mypy` é opcional agora; pode ser adicionado ao CI depois.

## 6. Pendências

- [ ] Confirmar **uv** vs pip.
- [ ] Patch exato do Python 3.14 e tag da imagem.
- [ ] Adotar mypy desde já?
