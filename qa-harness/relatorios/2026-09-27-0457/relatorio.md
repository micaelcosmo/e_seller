# Relatório de QA — e_seller

**Execução:** 2026-09-27-0457 · **Modo:** visual · **Viewports:** monitor · **Branch:** enrichment · **Commit:** 67eadb2 · **Motor:** 1.3.0

Gerado de `manifesto.yaml` pelo motor da skill `/qa`. Evidência de imagem: `evidencias.json` de cada pasta (PNG em base64; `python qa-harness/executar.py reverter` devolve os arquivos).

## Placar

| Veredito | Pontos |
|---|---|
| VALIDO | 14 |
| FALHA DE PRODUTO | 11 |
| EVIDENCIA INVALIDA | 0 |
| INCONCLUSIVO | 0 |

Healing: 0 ciclo(s) em 0 ponto(s).
Revisão de validade: 25 ponto(s) auditado(s), 6 veredito(s) alterado(s) em relação ao automático.

## Jornadas (prova visual das histórias)

| Jornada | História | Viewport | Passos | Veredito |
|---|---|---|---|---|
| Visitante cria uma conta e já entra | História 1 - Visitante cria uma conta de comprador | monitor | 16/16 | **VALIDO** |
| Comprador erra a senha, entra e sai da conta | História 2 - Comprador entra e sai da conta | monitor | 19/19 | **VALIDO** |
| Comprador salva o perfil fiscal | História 3 - Comprador mantém o perfil fiscal | monitor | 10/10 | **FALHA DE PRODUTO** |
| Administrador entra no painel pelo formulário de login | História 1 - Administrador entra no painel administrativo | monitor | 1/3 | **FALHA DE PRODUTO** (motor: EVIDENCIA INVALIDA) |
| Administrador vê a lista de e-books no painel | História 2 - Administrador cadastra e publica um e-book | monitor | 1/2 | **FALHA DE PRODUTO** (motor: EVIDENCIA INVALIDA) |
| Administrador vê os pedidos com status, valor e data | História 3 - Administrador acompanha as vendas | monitor | 1/3 | **FALHA DE PRODUTO** (motor: EVIDENCIA INVALIDA) |
| Administrador procura a avaliação pendente para moderar | História 4 - Administrador modera as avaliações | monitor | 1/2 | **FALHA DE PRODUTO** (motor: EVIDENCIA INVALIDA) |
| Administrador vê os cupons de desconto | História 5 - Administrador gerencia cupons de desconto | monitor | 1/2 | **FALHA DE PRODUTO** (motor: EVIDENCIA INVALIDA) |
| Comprador vê os e-books comprados e quem não comprou vê a biblioteca vazia | História 1 - Comprador baixa um e-book da biblioteca | monitor | 7/7 | **VALIDO** |
| Comprador marca um e-book com o coração e o vê nos favoritos | História 2 - Comprador guarda e-books nos favoritos | monitor | 6/6 | **VALIDO** |
| Comprador avalia um e-book que comprou e quem não comprou é recusado | História 3 - Comprador avalia um e-book que comprou | monitor | 10/10 | **VALIDO** |
| Comprador compra pelo carrinho, paga e recebe o e-book | História 1 - Comprador compra pelo carrinho e paga | monitor | 14/14 | **VALIDO** |
| Visitante compra informando só o e-mail | História 2 - Visitante compra um e-book sem ter conta | monitor | 6/7 | **FALHA DE PRODUTO** |
| Comprador confere um cupom de desconto | História 3 - Comprador usa um cupom de desconto | monitor | 6/6 | **VALIDO** |
| Comprador vê os pedidos e tenta pagar o pendente | História 4 - Comprador acompanha os pedidos e retoma um pagamento pendente | monitor | 6/6 | **FALHA DE PRODUTO** |
| Visitante conhece a loja e vê o catálogo | História 1 - Visitante conhece a loja e o catálogo | monitor | 6/6 | **VALIDO** |
| Visitante busca um e-book pelo título | História 2 - Visitante busca um e-book por título ou autor | monitor | 5/5 | **VALIDO** |
| Visitante ordena e filtra o catálogo por preço | História 3 - Visitante filtra e ordena o catálogo por preço | monitor | 6/6 | **VALIDO** |
| Visitante abre a página de um e-book | História 4 - Visitante vê o detalhe de um e-book | monitor | 9/9 | **VALIDO** |
| Visitante assina a newsletter pelo rodapé | História 5 - Visitante assina a newsletter | monitor | 4/4 | **VALIDO** |
| Visitante abre a política de privacidade e os termos pelo rodapé | História 6 - Visitante lê a política de privacidade e os termos | monitor | 3/6 | **FALHA DE PRODUTO** |

- **Jornada - Comprador salva o perfil fiscal**: 10/10 passos; 2 erro(s) de console. passo 10 (Vê a confirmação de perfil salvo): não achei "Perfil salvo" em body
- **Jornada - Administrador entra no painel pelo formulário de login**: 1/3 passos; 13 erro(s) de console. passo 1 (Abre o painel administrativo): não consegui abrir /admin/: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/
  - Revisão: Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Jornada - Administrador vê a lista de e-books no painel**: 1/2 passos; 13 erro(s) de console. passo 1 (Abre a lista de produtos): não consegui abrir /admin/product/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/product/list
  - Revisão: Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Jornada - Administrador vê os pedidos com status, valor e data**: 1/3 passos; 13 erro(s) de console. passo 1 (Abre a lista de pedidos): não consegui abrir /admin/order/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/order/list
  - Revisão: Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Jornada - Administrador procura a avaliação pendente para moderar**: 1/2 passos; 13 erro(s) de console. passo 1 (Abre a lista de avaliações): não consegui abrir /admin/review/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/review/list
  - Revisão: Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Jornada - Administrador vê os cupons de desconto**: 1/2 passos; 13 erro(s) de console. passo 1 (Abre a lista de cupons): não consegui abrir /admin/coupon/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/coupon/list
  - Revisão: Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Jornada - Visitante compra informando só o e-mail**: 6/7 passos. passo 6 (Chega à página de pagamento do pedido): a URL é http://127.0.0.1:48273/#/pedidos, esperava /pay/simulate/
- **Jornada - Comprador vê os pedidos e tenta pagar o pendente**: 6/6 passos. passo 6 (Vê como pagar o pedido pendente): não achei "Pagar" em .orders-list
- **Jornada - Visitante abre a política de privacidade e os termos pelo rodapé**: 3/6 passos. passo 3 (Vê a política de privacidade): não achei "Política de Privacidade" em body

## Base visual (retrato do sistema)

| Perfil | Viewport | Telas | Erros de console | Veredito |
|---|---|---|---|---|
| visitante | monitor | 7 | 13 | **FALHA DE PRODUTO** (motor: VALIDO) |
| cliente | monitor | 7 | 1 | **VALIDO** |
| sem_compras | monitor | 2 | 0 | **VALIDO** |
| admin | monitor | 7 | 15 | **FALHA DE PRODUTO** |

- **Base visual - admin (monitor)**: 01-painel falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/; 02-produtos falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/product/list; 03-pedidos falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/order/list; 04-avaliacoes falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/review/list; 05-cupons falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/coupon/list; 06-painel-html-de-pedidos renderizou só 28 caracteres; 07-painel-html-novo-ebook renderizou só 28 caracteres

## Ajuste/retorno para o desenvolvimento

### Achado 1 - Comprador salva o perfil fiscal

- **Origem:** Jornada - Comprador salva o perfil fiscal (acesso, jornada)
- **História:** História 3 - Comprador mantém o perfil fiscal
- **O que a evidência mostra:** 10/10 passos; 2 erro(s) de console. passo 10 (Vê a confirmação de perfil salvo): não achei "Perfil salvo" em body
- **Evidências:** `qa-harness/evidencias/jornadas/acesso/comprador-salva-perfil-fiscal/monitor/01-abre-minha-conta.png`, `qa-harness/evidencias/jornadas/acesso/comprador-salva-perfil-fiscal/monitor/02-ve-o-formulario-do-perfil-fiscal.png`, `qa-harness/evidencias/jornadas/acesso/comprador-salva-perfil-fiscal/monitor/03-digita-o-nome-completo.png`, `qa-harness/evidencias/jornadas/acesso/comprador-salva-perfil-fiscal/monitor/04-digita-o-cpf.png`, `qa-harness/evidencias/jornadas/acesso/comprador-salva-perfil-fiscal/monitor/05-digita-o-endereco.png`, `qa-harness/evidencias/jornadas/acesso/comprador-salva-perfil-fiscal/monitor/06-digita-a-cidade.png`

### Achado 2 - Administrador entra no painel pelo formulário de login

- **Origem:** Jornada - Administrador entra no painel pelo formulário de login (administracao, jornada)
- **História:** História 1 - Administrador entra no painel administrativo
- **O que a evidência mostra:** 1/3 passos; 13 erro(s) de console. passo 1 (Abre o painel administrativo): não consegui abrir /admin/: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/
- **Leitura da revisão:** Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Evidências:** `qa-harness/evidencias/jornadas/administracao/administrador-entra-no-painel/monitor/01-abre-o-painel-administrativo.png`

### Achado 3 - Administrador vê a lista de e-books no painel

- **Origem:** Jornada - Administrador vê a lista de e-books no painel (administracao, jornada)
- **História:** História 2 - Administrador cadastra e publica um e-book
- **O que a evidência mostra:** 1/2 passos; 13 erro(s) de console. passo 1 (Abre a lista de produtos): não consegui abrir /admin/product/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/product/list
- **Leitura da revisão:** Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Evidências:** `qa-harness/evidencias/jornadas/administracao/administrador-ve-os-produtos/monitor/01-abre-a-lista-de-produtos.png`

### Achado 4 - Administrador vê os pedidos com status, valor e data

- **Origem:** Jornada - Administrador vê os pedidos com status, valor e data (administracao, jornada)
- **História:** História 3 - Administrador acompanha as vendas
- **O que a evidência mostra:** 1/3 passos; 13 erro(s) de console. passo 1 (Abre a lista de pedidos): não consegui abrir /admin/order/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/order/list
- **Leitura da revisão:** Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Evidências:** `qa-harness/evidencias/jornadas/administracao/administrador-ve-os-pedidos/monitor/01-abre-a-lista-de-pedidos.png`

### Achado 5 - Administrador procura a avaliação pendente para moderar

- **Origem:** Jornada - Administrador procura a avaliação pendente para moderar (administracao, jornada)
- **História:** História 4 - Administrador modera as avaliações
- **O que a evidência mostra:** 1/2 passos; 13 erro(s) de console. passo 1 (Abre a lista de avaliações): não consegui abrir /admin/review/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/review/list
- **Leitura da revisão:** Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Evidências:** `qa-harness/evidencias/jornadas/administracao/administrador-ve-a-fila-de-moderacao/monitor/01-abre-a-lista-de-avaliacoes.png`

### Achado 6 - Administrador vê os cupons de desconto

- **Origem:** Jornada - Administrador vê os cupons de desconto (administracao, jornada)
- **História:** História 5 - Administrador gerencia cupons de desconto
- **O que a evidência mostra:** 1/2 passos; 13 erro(s) de console. passo 1 (Abre a lista de cupons): não consegui abrir /admin/coupon/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/coupon/list
- **Leitura da revisão:** Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Evidências:** `qa-harness/evidencias/jornadas/administracao/administrador-ve-os-cupons/monitor/01-abre-a-lista-de-cupons.png`

### Achado 7 - Visitante compra informando só o e-mail

- **Origem:** Jornada - Visitante compra informando só o e-mail (compra, jornada)
- **História:** História 2 - Visitante compra um e-book sem ter conta
- **O que a evidência mostra:** 6/7 passos. passo 6 (Chega à página de pagamento do pedido): a URL é http://127.0.0.1:48273/#/pedidos, esperava /pay/simulate/
- **Evidências:** `qa-harness/evidencias/jornadas/compra/visitante-compra-sem-conta/monitor/01-abre-o-e-book-python-na-pratica.png`, `qa-harness/evidencias/jornadas/compra/visitante-compra-sem-conta/monitor/02-clica-em-comprar-e-baixar-sem-e-mail.png`, `qa-harness/evidencias/jornadas/compra/visitante-compra-sem-conta/monitor/03-ve-o-pedido-de-e-mail-valido.png`, `qa-harness/evidencias/jornadas/compra/visitante-compra-sem-conta/monitor/04-digita-o-e-mail.png`, `qa-harness/evidencias/jornadas/compra/visitante-compra-sem-conta/monitor/05-clica-em-comprar-e-baixar.png`, `qa-harness/evidencias/jornadas/compra/visitante-compra-sem-conta/monitor/06-chega-a-pagina-de-pagamento-do-pedido.png`

### Achado 8 - Comprador vê os pedidos e tenta pagar o pendente

- **Origem:** Jornada - Comprador vê os pedidos e tenta pagar o pendente (compra, jornada)
- **História:** História 4 - Comprador acompanha os pedidos e retoma um pagamento pendente
- **O que a evidência mostra:** 6/6 passos. passo 6 (Vê como pagar o pedido pendente): não achei "Pagar" em .orders-list
- **Evidências:** `qa-harness/evidencias/jornadas/compra/comprador-retoma-pedido-pendente/monitor/01-abre-a-loja-com-a-conta.png`, `qa-harness/evidencias/jornadas/compra/comprador-retoma-pedido-pendente/monitor/02-clica-em-pedidos.png`, `qa-harness/evidencias/jornadas/compra/comprador-retoma-pedido-pendente/monitor/03-ve-a-lista-de-pedidos.png`, `qa-harness/evidencias/jornadas/compra/comprador-retoma-pedido-pendente/monitor/04-ve-o-pedido-pendente.png`, `qa-harness/evidencias/jornadas/compra/comprador-retoma-pedido-pendente/monitor/05-ve-o-valor-do-pedido.png`, `qa-harness/evidencias/jornadas/compra/comprador-retoma-pedido-pendente/monitor/06-ve-como-pagar-o-pedido-pendente.png`

### Achado 9 - Visitante abre a política de privacidade e os termos pelo rodapé

- **Origem:** Jornada - Visitante abre a política de privacidade e os termos pelo rodapé (vitrine, jornada)
- **História:** História 6 - Visitante lê a política de privacidade e os termos
- **O que a evidência mostra:** 3/6 passos. passo 3 (Vê a política de privacidade): não achei "Política de Privacidade" em body
- **Evidências:** `qa-harness/evidencias/jornadas/vitrine/visitante-le-privacidade-e-termos/monitor/01-abre-a-loja.png`, `qa-harness/evidencias/jornadas/vitrine/visitante-le-privacidade-e-termos/monitor/02-clica-em-privacidade-no-rodape.png`, `qa-harness/evidencias/jornadas/vitrine/visitante-le-privacidade-e-termos/monitor/03-ve-a-politica-de-privacidade.png`

### Achado 10 - Base visual - visitante (monitor)

- **Origem:** Base visual - visitante (monitor) (base-visual, base)
- **História:** Base visual - visitante
- **O que a evidência mostra:** 7 tela(s) em monitor; 13 erro(s) de console. Todas renderizaram conteúdo, sem rolagem horizontal.
- **Leitura da revisão:** `/privacidade` e `/termos` renderizam a home do SPA; título da aba herdado da página do e-book em carrinho e 404.
- **Evidências:** `qa-harness/evidencias/_base/visitante/monitor/01-home.png`, `qa-harness/evidencias/_base/visitante/monitor/02-detalhe-do-ebook.png`, `qa-harness/evidencias/_base/visitante/monitor/03-carrinho-sem-conta.png`, `qa-harness/evidencias/_base/visitante/monitor/04-pagina-inexistente.png`, `qa-harness/evidencias/_base/visitante/monitor/05-privacidade.png`, `qa-harness/evidencias/_base/visitante/monitor/06-termos.png`

### Achado 11 - Base visual - admin (monitor)

- **Origem:** Base visual - admin (monitor) (base-visual, base)
- **História:** Base visual - admin
- **O que a evidência mostra:** 7 tela(s) em monitor; 15 erro(s) de console. Problemas: 01-painel falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/; 02-produtos falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/product/list; 03-pedidos falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/order/list; 04-avaliacoes falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/review/list; 05-cupons falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/coupon/list; 06-painel-html-de-pedidos renderizou só 28 caracteres; 07-painel-html-novo-ebook renderizou só 28 caracteres
- **Evidências:** `qa-harness/evidencias/_base/admin/monitor/01-painel.png`, `qa-harness/evidencias/_base/admin/monitor/02-produtos.png`, `qa-harness/evidencias/_base/admin/monitor/03-pedidos.png`, `qa-harness/evidencias/_base/admin/monitor/04-avaliacoes.png`, `qa-harness/evidencias/_base/admin/monitor/05-cupons.png`, `qa-harness/evidencias/_base/admin/monitor/06-painel-html-de-pedidos.png`

## Lacunas de especificação (lint das histórias)

Nenhuma: toda jornada cita história existente, verifica o resultado e marca INICIO e FIM.

## Revisão de validade e healing

Execução de healing (ciclo 1) da rodada 1 — mesmo build do produto, adaptador corrigido. Os vereditos consolidados da rodada estão em 2026-09-27-0433/revisao.yaml; aqui só se reclassificam os mesmos pontos pelo mesmo motivo.

- **Jornada - Administrador entra no painel pelo formulário de login**: EVIDENCIA INVALIDA → FALHA DE PRODUTO · healing 0 — Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Jornada - Administrador vê a lista de e-books no painel**: EVIDENCIA INVALIDA → FALHA DE PRODUTO · healing 0 — Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Jornada - Administrador vê os pedidos com status, valor e data**: EVIDENCIA INVALIDA → FALHA DE PRODUTO · healing 0 — Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Jornada - Administrador procura a avaliação pendente para moderar**: EVIDENCIA INVALIDA → FALHA DE PRODUTO · healing 0 — Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Jornada - Administrador vê os cupons de desconto**: EVIDENCIA INVALIDA → FALHA DE PRODUTO · healing 0 — Navegação recusada por causa do produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx).
- **Base visual - visitante (monitor)**: VALIDO → FALHA DE PRODUTO · healing 0 — `/privacidade` e `/termos` renderizam a home do SPA; título da aba herdado da página do e-book em carrinho e 404.

## Criados nesta execução

Nada criado — execução sobre artefatos existentes.

