# 17 — Fluxo Spec-Driven Development (SDD)

> Documento de planning · e_seller · 2026-06-06
> Como Spec → Teste → Código opera, na prática, no dia a dia.

---

## 1. Princípio

**Nenhuma linha de código de produção sem uma spec que a justifique.**
A spec descreve o comportamento; o teste o verifica; o código o implementa.

## 2. O ciclo completo (SDD + TDD juntos)

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  1. SPEC │ → │ 2. REVISA│ → │ 3. TESTE │ → │ 4. CÓDIGO│ → │ 5. REFAC.│
│ escrever │   │ aprovar  │   │ (RED)    │   │ (GREEN)  │   │ + docs   │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
                                    ▲                              │
                                    └──────── repete por cenário ──┘
```

1. **Spec:** criar/atualizar documento em `.spec/` descrevendo o comportamento
   (com cenários de aceite, estilo [`05-user-stories.md`](05-user-stories.md)).
2. **Revisão/aprovação:** validar a spec **antes** de codar (evita retrabalho).
3. **Teste (RED):** escrever o teste do cenário → falha.
4. **Código (GREEN):** mínimo para passar.
5. **Refactor + docs:** limpar o código; atualizar spec/STATUS/CHANGELOG se preciso.

## 3. Onde cada coisa vive

| Artefato | Lugar |
|---|---|
| Specs de planejamento | `.spec/planning/` (fase atual) |
| Specs de implementação (futuro) | `.spec/` (ex.: `.spec/features/...`) |
| Testes | junto do código (`tests/`, por módulo de domínio) |
| Decisões arquiteturais | ADRs em `.spec/` (ver [`07-adr-stack.md`](07-adr-stack.md)) |

## 4. Estrutura sugerida de uma spec de feature (futuro)

```
# Feature: <nome>
## Contexto / motivação
## Comportamento (cenários Gherkin)
## Regras de negócio / invariantes
## Impacto (modelos, rotas, migrations)
## Fora de escopo
## Rastreabilidade (RF/RNF, stories)
```

## 5. Mudou o comportamento? Atualize a spec primeiro

Qualquer alteração de comportamento começa **editando a spec**, depois o teste,
depois o código. Spec e código nunca divergem por muito tempo.

## 6. Relação com o Git/PR

- A spec entra no **mesmo PR** da implementação (ou antes, num PR de spec).
- Revisão de PR confere: spec presente, testes antes, CI verde
  (ver [`16-definition-of-done.md`](16-definition-of-done.md)).

## 7. Quando o planning termina

Esta fase (`.spec/planning/`) se encerra quando:
- [ ] Todos os documentos de planning estão escritos e revisados.
- [ ] As decisões em aberto estão resolvidas (ou conscientemente adiadas).
- [ ] O Micael **aprova** seguir para a próxima etapa (specs de implementação + código).

> Até lá, **trabalhamos só aqui** (regra de ouro do [`CLAUDE.md`](../../CLAUDE.md)).
