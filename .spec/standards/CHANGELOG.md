# CHANGELOG — .spec/standards/

> Histórico dos padrões de engenharia. Atualizar a cada mudança de regra.
> Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

---

## [Não lançado]

### Adicionado — 2026-06-07
- `docstrings-and-language.md`: código em inglês; **docstrings/comentários em pt-BR**
  obrigatórios; **docstring em TODA funcionalidade**; arquivos UTF-8 (evitar problemas
  de encode/decode).
- `oop-and-naming.md` (seção 4): **regras estruturais** — sem `def` dentro de `def`,
  sem arquivo só com funções (usar classe/`__call__`), sem classe dentro de classe;
  exceção mínima documentada para handlers/dependencies do FastAPI.
- `CHANGELOG.md` próprio desta trilha.

### Adicionado — 2026-06-06 (criação)
- `README`, `python-and-tooling`, `pep8-and-imports`, `solid`, `oop-and-naming`, `enforcement`.
- Decisões: SOLID, POO sem globais, services = classe com DI, laços explícitos
  (sem comprehension/lambda), naming declarativo, Python 3.14.5+, enforcement
  Ruff + pre-commit + revisão.

---

_Início da trilha de standards: 2026-06-06_
