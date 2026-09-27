# Relatório de QA — e_seller

**Execução:** 2026-09-27-0601 · **Modo:** responsividade · **Viewports:** notebook, celular · **Branch:** enrichment · **Commit:** 67eadb2 · **Motor:** 1.3.0

Gerado de `manifesto.yaml` pelo motor da skill `/qa`. Evidência de imagem: `evidencias.json` de cada pasta (PNG em base64; `python qa-harness/executar.py reverter` devolve os arquivos).

## Placar

| Veredito | Pontos |
|---|---|
| VALIDO | 6 |
| FALHA DE PRODUTO | 2 |
| EVIDENCIA INVALIDA | 0 |
| INCONCLUSIVO | 0 |

Healing: 0 ciclo(s) em 0 ponto(s).
Revisão de validade: 8 ponto(s) auditado(s), 0 veredito(s) alterado(s) em relação ao automático.

## Base visual (retrato do sistema)

| Perfil | Viewport | Telas | Erros de console | Veredito |
|---|---|---|---|---|
| visitante | notebook | 7 | 0 | **VALIDO** |
| cliente | notebook | 7 | 1 | **VALIDO** |
| sem_compras | notebook | 2 | 0 | **VALIDO** |
| admin | notebook | 7 | 2 | **FALHA DE PRODUTO** |
| visitante | celular | 7 | 0 | **VALIDO** |
| cliente | celular | 7 | 1 | **VALIDO** |
| sem_compras | celular | 2 | 0 | **VALIDO** |
| admin | celular | 7 | 2 | **FALHA DE PRODUTO** |

- **Base visual - admin (notebook)**: 04-avaliacoes tem rolagem horizontal (1624px > 1366px); 06-painel-html-de-pedidos renderizou só 28 caracteres; 07-painel-html-novo-ebook renderizou só 28 caracteres
- **Base visual - admin (celular)**: 01-painel renderizou só 23 caracteres; 06-painel-html-de-pedidos renderizou só 28 caracteres; 07-painel-html-novo-ebook renderizou só 28 caracteres

## Responsividade

Viewports: notebook, celular.

- Base visual - admin (notebook): 04-avaliacoes tem rolagem horizontal (1624px > 1366px)
- Base visual - admin (notebook): 06-painel-html-de-pedidos renderizou só 28 caracteres
- Base visual - admin (notebook): 07-painel-html-novo-ebook renderizou só 28 caracteres
- Base visual - admin (celular): 01-painel renderizou só 23 caracteres
- Base visual - admin (celular): 06-painel-html-de-pedidos renderizou só 28 caracteres
- Base visual - admin (celular): 07-painel-html-novo-ebook renderizou só 28 caracteres

## Ajuste/retorno para o desenvolvimento

### Achado 1 - Base visual - admin (notebook)

- **Origem:** Base visual - admin (notebook) (base-visual, base)
- **História:** Base visual - admin
- **O que a evidência mostra:** 7 tela(s) em notebook; 2 erro(s) de console. Problemas: 04-avaliacoes tem rolagem horizontal (1624px > 1366px); 06-painel-html-de-pedidos renderizou só 28 caracteres; 07-painel-html-novo-ebook renderizou só 28 caracteres
- **Leitura da revisão:** `04-avaliacoes` com rolagem horizontal (1624px > 1366px): comentário inteiro e data com microssegundos na lista do painel — corrigido depois desta execução (comentário resumido em 60 caracteres e data curta, com teste). `06`/`07` são os painéis HTML da decisão bloqueante D18.
- **Evidências:** `qa-harness/evidencias/_base/admin/notebook/01-painel.png`, `qa-harness/evidencias/_base/admin/notebook/02-produtos.png`, `qa-harness/evidencias/_base/admin/notebook/03-pedidos.png`, `qa-harness/evidencias/_base/admin/notebook/04-avaliacoes.png`, `qa-harness/evidencias/_base/admin/notebook/05-cupons.png`, `qa-harness/evidencias/_base/admin/notebook/06-painel-html-de-pedidos.png`

### Achado 2 - Base visual - admin (celular)

- **Origem:** Base visual - admin (celular) (base-visual, base)
- **História:** Base visual - admin
- **O que a evidência mostra:** 7 tela(s) em celular; 2 erro(s) de console. Problemas: 01-painel renderizou só 23 caracteres; 06-painel-html-de-pedidos renderizou só 28 caracteres; 07-painel-html-novo-ebook renderizou só 28 caracteres
- **Leitura da revisão:** `01-painel` com 23 caracteres é tela curta por desenho do SQLAdmin (a página inicial do painel não tem conteúdo e o menu vai para o hambúrguer) — não é defeito. A falha que resta é a dos painéis HTML `06`/`07` (D18).
- **Evidências:** `qa-harness/evidencias/_base/admin/celular/01-painel.png`, `qa-harness/evidencias/_base/admin/celular/02-produtos.png`, `qa-harness/evidencias/_base/admin/celular/03-pedidos.png`, `qa-harness/evidencias/_base/admin/celular/04-avaliacoes.png`, `qa-harness/evidencias/_base/admin/celular/05-cupons.png`, `qa-harness/evidencias/_base/admin/celular/06-painel-html-de-pedidos.png`

## Lacunas de especificação (lint das histórias)

Nenhuma: toda jornada cita história existente, verifica o resultado e marca INICIO e FIM.

## Revisão de validade e healing

`/qa responsividade` (base visual em notebook 1366px e celular 390px, 4 perfis) sobre o build da rodada 3 + respiro das capas no carrinho/biblioteca. Foco: quebra de layout, rolagem horizontal e elemento inacessível. Loja (visitante, cliente, sem_compras): nenhuma tela com rolagem horizontal (`scrollWidth` = `innerWidth` em todas), textos e ações visíveis; no celular a app bar fica em duas linhas com o menu em folha, grade em 2 colunas, carrossel com rolagem lateral.

- **Base visual - admin (notebook)**: FALHA DE PRODUTO → FALHA DE PRODUTO · healing 0 — `04-avaliacoes` com rolagem horizontal (1624px > 1366px): comentário inteiro e data com microssegundos na lista do painel — corrigido depois desta execução (comentário resumido em 60 caracteres e data curta, com teste). `06`/`07` são os painéis HTML da decisão bloqueante D18.
- **Base visual - admin (celular)**: FALHA DE PRODUTO → FALHA DE PRODUTO · healing 0 — `01-painel` com 23 caracteres é tela curta por desenho do SQLAdmin (a página inicial do painel não tem conteúdo e o menu vai para o hambúrguer) — não é defeito. A falha que resta é a dos painéis HTML `06`/`07` (D18).

## Criados nesta execução

Nada criado — execução sobre artefatos existentes.

