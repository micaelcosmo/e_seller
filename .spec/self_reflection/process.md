# Processo de Auto-Reflexão

> Trilha self_reflection · e_seller · 2026-06-07

---

## 1. Quando refletir

- **Antes** de desenvolver: registrar suposições, escopo e riscos do que vou fazer.
- **Durante:** checagem rápida ao concluir cada parte significativa.
- **Depois:** retrospectiva da tarefa/marco (o que ficou bom, o que não, ações).

## 2. Checklist de auto-reflexão

**Padrões ([`../standards/`](../standards/))**
- [ ] Código em inglês; docstrings/comentários em pt-BR; UTF-8.
- [ ] Docstring em TODA funcionalidade.
- [ ] Sem `def`-in-`def`, sem arquivo só com funções, sem classe aninhada.
- [ ] Sem comprehension/lambda; laços `for` explícitos.
- [ ] Naming declarativo; imports na hierarquia.

**Arquitetura/SOLID**
- [ ] Services = classes com DI; integrações atrás de Protocol.
- [ ] Responsabilidade única; sem estado global.

**TDD/qualidade**
- [ ] Teste escrito antes (Red→Green); cenários da unit cobertos.
- [ ] Ruff e testes verdes.

**Segurança**
- [ ] Controles testados (RNF-01/02/03/20; auth; path traversal).
- [ ] Sem segredos no código.

**Coerência**
- [ ] Spec ↔ código alinhados; UML/CHANGELOG atualizados.
- [ ] Simplificações possíveis? Código morto?

## 3. Formato da entrada (em `log.md`)

```
## AAAA-MM-DD — <tarefa/marco>
**Fiz:** ...
**Bom:** ...
**A melhorar / dívidas:** ...
**Suposições assumidas:** ...
**Ações (viram tarefa/teste/risco):** ...
```

## 4. Princípios

- **Honestidade primeiro:** registrar o que está incerto/errado, não só o que está certo.
- Reflexão é leve e frequente; o `/code-review` (multi-agente) é o aprofundamento sob demanda.
- Ações concretas viram tarefas, testes ou riscos (alimenta [`../dashboard/`](../dashboard/)).
