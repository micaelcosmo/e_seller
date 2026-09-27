# Convenção de comentários

**Status:** vigente · **Modelo:** skill `/qa` · **Validado por:** coletor do motor
(`python qa-harness/executar.py comentarios`) + julgamento por IA na etapa
`/qa comentarios`. O resultado entra no relatório como **warning** — nunca
derruba a execução.

## A regra em uma frase

**O código explica o que ele faz agora. A história de como chegou aqui mora no `.md`.**

## O que NÃO vai no código

| Conceito | Onde mora |
|---|---|
| Changelog ("antes fazia X, agora faz Y", "isto mudou em…") | <!-- PREENCHER: changelog / status do projeto --> |
| Decisão e o porquê dela | <!-- PREENCHER: ADR / registro de decisões --> |
| Fluxo de dados ou de tela | <!-- PREENCHER: spec de fluxos, se houver --> |
| História de usuário e critério de aceite | `spec/test/historias/` |
| Achado de QA, bug encontrado, healing | `qa-harness/relatorios/<execução>/relatorio.md` e `spec/qa/` |
| Plano do que falta, TODO com prazo | <!-- PREENCHER: planejamento / board --> |

Sinais de que um comentário conta história e deveria sair do código: data,
número de fase ou versão; verbo no passado sobre o próprio código (*era, fazia,
virou, saiu daqui, divergia, quebrava, passou a*); palavras de processo (*achado,
decisão, pedido, regressão, descoberto, healing*); explicação de bug já corrigido.

## O que PODE ficar no código

Comentário que ajuda quem lê **esta linha, hoje**: a razão não óbvia de uma
escolha, no presente; uma restrição externa; um ponteiro curto para o documento
que tem a história. Regra prática: **se continuar verdadeiro daqui a um ano sem
contexto histórico, pode ficar.**

## Convenção por linguagem

- **Python:** docstring (`"""…"""`) em módulo, classe e função públicas — nunca um
  bloco de `#` acima da assinatura fazendo papel de docstring. `#` só para nota
  curta dentro do corpo.
- **JavaScript / TypeScript:** JSDoc (`/** … */`) quando a função tem contrato a
  documentar; `//` para nota curta junto do trecho. Bloco de `//` com mais de três
  linhas virou documento: mova.
- **CSS:** `/* … */` para separar seções ou explicar um valor mágico. Nada de
  histórico de ajuste de layout.
- **YAML de spec** é documentação: pode ter contexto e decisão no cabeçalho.

## Código comentado

Não se comenta código para guardar — o git guarda. Bloco comentado é removido; se
for uma opção futura, vira linha no planejamento.

## Como o `/qa` verifica

1. O coletor varre os alvos de `comentarios` do `qa-harness/config.yaml` e
   classifica cada suspeito em `narrativa` · `codigo-comentado` · `convencao` · `bloco-longo`.
2. A saída é candidato, não veredito: a IA julga cada caso (`violacao` ou `aceitavel`).
3. O que sobra vira warning na seção "Warnings - Convenção de comentários" do
   `relatorio.md`, com arquivo, linha e para qual `.md` o conteúdo deveria migrar.
