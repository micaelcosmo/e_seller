# Enforcement (como cumprir os padrões)

> Padrão · e_seller · 2026-06-06
> Combinação: **automático (Ruff/CI) + pre-commit + revisão de PR**.

---

## 1. Camadas de cobrança

| Camada | Cobre | Quando |
|---|---|---|
| **Ruff** (lint + format) | PEP 8, imports/hierarquia, nomes (`N`), bugs comuns (`B`, `F`), `UP`, `ASYNC` | local + CI |
| **pre-commit** | Roda Ruff (e checagens rápidas) | antes de cada commit |
| **CI** | Ruff + pytest + cobertura | a cada push/PR |
| **Revisão de PR** | O que não é automatizável (POO, SOLID, naming declarativo, **sem comprehension/lambda**) | antes do merge |

## 2. O que é automático vs. revisão

**Automático (Ruff/CI):**
- Formatação, indentação, `line-length`.
- Hierarquia/ordem de imports (`I`).
- Convenções de nome básicas (`N`).
- Erros e *code smells* (`F`, `B`, `PL` parcial).

**Revisão manual (não há regra confiável no Ruff):**
- **Proibição de list/dict comprehension** (não habilitamos `C4`).
- Uso de `lambda` (convenção: banido).
- Aderência a **SOLID** e **injeção de dependência** no `__init__`.
- Ausência de variáveis globais / estado de módulo.
- Naming **declarativo** (`produto`, não `prod_x`).

## 3. Checklist de revisão de PR (padrões)

- [ ] Services são **classes** com dependências injetadas no `__init__`.
- [ ] **Sem** variáveis globais / estado mutável de módulo.
- [ ] **Sem** comprehension e **sem** `lambda` (laços `for` explícitos).
- [ ] Nomes **declarativos** e completos.
- [ ] Integrações externas atrás de **Protocol** (testáveis com fake).
- [ ] Imports na hierarquia correta (já validado pelo Ruff, conferir mesmo assim).
- [ ] Ruff e testes verdes no CI.

## 4. Config de pre-commit (proposta — `.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: <fixar versão>
    hooks:
      - id: ruff          # lint
      - id: ruff-format   # format
```

## 5. Pendências

- [ ] Fixar versão do hook do Ruff.
- [ ] Incluir cobertura mínima como gate (ver [`../planning/15-ci-cd.md`](../planning/15-ci-cd.md)).
