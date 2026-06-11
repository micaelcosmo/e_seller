# 14 — Padrões de Código

> ⚠️ **SUPERADO (2026-06-06):** este documento (congelado, fase de planning) foi
> substituído pelos padrões vivos em [`../standards/`](../standards/), que incluem
> SOLID, POO, services como classes com DI, laços explícitos (sem comprehension/lambda)
> e nomenclatura declarativa. Mantido aqui apenas como registro histórico.

> Documento de planning · e_seller · 2026-06-06
> Estilo, ferramentas e convenções. Base: **PEP 8** (obrigatório por CLAUDE.md).

---

## 1. PEP 8 + Ruff

- Todo Python segue **PEP 8**.
- **Ruff** faz lint **e** formatação (substitui flake8/isort/black com uma só ferramenta, rápida e gratuita).
- O CI **falha** se houver violação (RNF-30).

> 💡 *O que é o Ruff?* Um linter/formatter em Rust, muito rápido, que aplica as
> regras do PEP 8 e organiza imports. Rodamos `ruff check` (lint) e `ruff format`.

### Config proposta (`pyproject.toml`)
```toml
[tool.ruff]
line-length = 88
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "ASYNC"]  # erros, pyflakes, imports, bugbear, pyupgrade, async
```

## 2. Type hints

- Usar **type hints** em funções de service e assinaturas públicas.
- `mypy` (opcional, gratuito) pode ser adicionado depois para checagem estática.

## 3. Convenções de nomenclatura

| Item | Convenção | Exemplo |
|---|---|---|
| Módulos/pacotes | `snake_case` | `payments/services.py` |
| Classes | `PascalCase` | `DownloadGrant` |
| Funções/variáveis | `snake_case` | `mark_paid()` |
| Constantes | `UPPER_SNAKE` | `MAX_DOWNLOADS` |
| Módulos de domínio | curtos, no singular do domínio | `catalog`, `orders` |

## 4. Organização (lembrete da arquitetura)

- Regras de negócio em **services**, não em views/models.
- Integrações externas isoladas e **mockáveis**.
- Ver [`08-arquitetura.md`](08-arquitetura.md).

## 5. Docstrings e comentários

- Docstrings em services e funções não triviais (o "porquê", não o "o quê").
- Comentários explicam decisões; código auto-explicativo dispensa comentário óbvio.
- Idioma: **pt-BR** em docs; código/identificadores podem ficar em inglês (convenção comum no ecossistema Python/FastAPI).

## 6. Commits

- Mensagens descritivas; referenciar spec/story quando aplicável
  (ex.: `feat(payments): webhook idempotente (US-05)`).
- Formato sugerido: **Conventional Commits** (`feat`, `fix`, `test`, `docs`, `refactor`, `chore`).

## 7. Revisão de código (PR)

Checklist mínimo:
- [ ] Existe spec/story vinculada (SDD).
- [ ] Testes escritos antes e passando (TDD).
- [ ] Ruff sem erros.
- [ ] Sem segredos no diff.
- [ ] STATUS/CHANGELOG atualizados se for marco.

## 8. Pre-commit (opcional, recomendado)

`pre-commit` rodando Ruff e checagens rápidas antes de cada commit — evita "quebrar o CI".
Gratuito; configurável em `.pre-commit-config.yaml`.

## 9. Pendências

- [ ] Adotar mypy desde o início ou depois?
- [ ] `line-length` 88 (padrão) confirmado?
