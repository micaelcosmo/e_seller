# .spec/standards/

Padrões de engenharia do e_seller — **vivos** (evoluem com o projeto) e
**obrigatórios**. Qualquer agente (humano ou IA) lê isto antes de escrever código.
Referenciado por [`../../CLAUDE.md`](../../CLAUDE.md).

> Os trechos de código aqui são **exemplos ilustrativos** do padrão, não o app.

## Documentos

| Doc | Assunto |
|---|---|
| [`python-and-tooling.md`](python-and-tooling.md) | Versão do Python, gerenciador de deps, Ruff, pytest. |
| [`pep8-and-imports.md`](pep8-and-imports.md) | PEP 8 e **hierarquia de imports**. |
| [`solid.md`](solid.md) | Princípios SOLID aplicados à nossa arquitetura. |
| [`oop-and-naming.md`](oop-and-naming.md) | POO, sem globais, `self.` no `__init__`, nomenclatura declarativa, sem comprehension/lambda, **regras estruturais**. |
| [`docstrings-and-language.md`](docstrings-and-language.md) | Código em inglês; docstrings/comentários em pt-BR (obrigatório); UTF-8. |
| [`enforcement.md`](enforcement.md) | O que é automático (Ruff/CI/pre-commit) vs. revisão. |

## Regras-âncora (resumo)

1. **PEP 8** sempre; imports agrupados por hierarquia, com linha em branco entre grupos.
2. **SOLID** sempre.
3. **POO**: pense em objetos; **sem variáveis globais**; atributos via `self.` no `__init__`.
4. **Nomenclatura declarativa**: `produto = ...`, nunca `prod_x = ...`.
5. **Laços explícitos**: `for produto in produtos:` — **proibido** list/dict comprehension e `lambda`.
6. **Services como classes** com injeção de dependência no construtor.
7. **Código em inglês; docstrings/comentários em pt-BR** (UTF-8). **Docstring em TODA funcionalidade.**
8. **Sem `def` dentro de `def`**, **sem arquivo só com funções** (use classe), **sem classe dentro de classe**.

> Estes padrões **substituem** o resumo congelado em
> [`../planning/14-padroes-de-codigo.md`](../planning/14-padroes-de-codigo.md).
