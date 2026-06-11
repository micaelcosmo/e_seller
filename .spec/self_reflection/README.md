# .spec/self_reflection/

Trilha **viva** de **auto-reflexão sobre o código** — uma prática em que o agente
(Claude) revisa criticamente o que produziu, com honestidade, **antes/durante/depois**
de cada desenvolvimento.

> Não é frontend. Não substitui o `/code-review` (revisão multi-agente sob demanda):
> é um **auto-check leve, contínuo e honesto** do próprio trabalho, em pt-BR.

## Documentos

| Doc | Assunto |
|---|---|
| [`process.md`](process.md) | Quando refletir, checklist, formato da entrada, ações. |
| [`log.md`](log.md) | Registro cronológico das auto-reflexões. |

## Por que existe

- Pegar cedo: divergência spec↔código, violação de padrões, falta de docstring/teste,
  oportunidades de simplificação, suposições assumidas.
- Alimentar o [dashboard](../dashboard/) (qualidade/decisões) e os
  [riscos](../planning/22-matriz-de-riscos.md).
- Manter a honestidade: registrar o que **não** está certo/claro, não só o que está.

## Regra de manutenção

A cada tarefa de desenvolvimento relevante, adicionar uma entrada em [`log.md`](log.md)
e registrar no [`CHANGELOG.md`](CHANGELOG.md).
