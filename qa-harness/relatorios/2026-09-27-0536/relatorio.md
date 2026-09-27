# Relatório de QA — e_seller

**Execução:** 2026-09-27-0536 · **Modo:** integracao · **Viewports:** monitor · **Branch:** enrichment · **Commit:** 67eadb2 · **Motor:** 1.3.0

Gerado de `manifesto.yaml` pelo motor da skill `/qa`. Evidência de imagem: `evidencias.json` de cada pasta (PNG em base64; `python qa-harness/executar.py reverter` devolve os arquivos).

## Placar

| Veredito | Pontos |
|---|---|
| VALIDO | 53 |
| FALHA DE PRODUTO | 0 |
| EVIDENCIA INVALIDA | 0 |
| INCONCLUSIVO | 0 |

Healing: 0 ciclo(s) em 0 ponto(s).
Revisão de validade: 53 ponto(s) auditado(s), 0 veredito(s) alterado(s) em relação ao automático.

## Integração

### Domínio acesso

- **Ponto 1 - Cadastro cria conta de comprador** — **VALIDO**
  - História: História 1 - Visitante cria uma conta de comprador
  - Leitura: O cadastro responde 201 com o e-mail enviado e o papel `customer`.
  - Evidências: `qa-harness/evidencias/api/acesso/01-cadastro.json`
- **Ponto 2 - E-mail já cadastrado é recusado** — **VALIDO**
  - História: História 1 - Visitante cria uma conta de comprador
  - Leitura: O segundo cadastro com o mesmo e-mail responde 409 "E-mail já cadastrado".
  - Evidências: `qa-harness/evidencias/api/acesso/02-cadastro-duplicado.json`
- **Ponto 3 - Login com senha correta devolve os tokens** — **VALIDO**
  - História: História 2 - Comprador entra e sai da conta
  - Leitura: O login responde 200 com `access_token` e `refresh_token` (mascarados na evidência).
  - Evidências: `qa-harness/evidencias/api/acesso/03-login-correto.json`
- **Ponto 4 - Senha errada é recusada** — **VALIDO**
  - História: História 2 - Comprador entra e sai da conta
  - Leitura: A senha errada responde 401 "Credenciais inválidas".
  - Evidências: `qa-harness/evidencias/api/acesso/04-login-senha-errada.json`
- **Ponto 5 - Token do logout deixa de valer** — **VALIDO**
  - História: História 2 - Comprador entra e sai da conta
  - Leitura: O `/me` responde 200 antes do logout e 401 com o mesmo token depois.
  - Evidências: `qa-harness/evidencias/api/acesso/05-me-antes-do-logout.json`, `qa-harness/evidencias/api/acesso/06-logout.json`, `qa-harness/evidencias/api/acesso/07-me-depois-do-logout.json`
- **Ponto 6 - Perfil fiscal enviado como a tela envia é salvo** — **VALIDO**
  - História: História 3 - Comprador mantém o perfil fiscal
  - Leitura: O perfil fiscal com o corpo da tela é salvo (200).
  - Evidências: `qa-harness/evidencias/api/acesso/08-perfil-fiscal-da-tela.json`
- **Ponto 7 - Perfil fiscal sem login é recusado** — **VALIDO**
  - História: História 3 - Comprador mantém o perfil fiscal
  - Leitura: Sem sessão o perfil fiscal responde 401.
  - Evidências: `qa-harness/evidencias/api/acesso/09-perfil-fiscal-sem-login.json`
### Domínio administracao

- **Ponto 1 - Comprador não acessa a administração** — **VALIDO**
  - História: História 1 - Administrador entra no painel administrativo
  - Leitura: `cliente` recebe 403 na API de administração.
  - Evidências: `qa-harness/evidencias/api/administracao/01-admin-como-comprador.json`
- **Ponto 2 - Sem login a administração recusa** — **VALIDO**
  - História: História 1 - Administrador entra no painel administrativo
  - Leitura: `visitante` recebe 401 na API de administração.
  - Evidências: `qa-harness/evidencias/api/administracao/02-admin-sem-login.json`
- **Ponto 3 - Formulário de login do painel abre o painel** — **VALIDO**
  - História: História 1 - Administrador entra no painel administrativo
  - Leitura: Sem token o login é recusado (403); com o token que a página põe no formulário ele redireciona para o painel `/admin/`.
  - Evidências: `qa-harness/evidencias/api/administracao/03-painel-formulario-de-login.json`, `qa-harness/evidencias/api/administracao/04-painel-login-sem-csrf.json`, `qa-harness/evidencias/api/administracao/05-painel-enviar-login.json`
- **Ponto 4 - E-book novo nasce como rascunho fora da vitrine** — **VALIDO**
  - História: História 2 - Administrador cadastra e publica um e-book
  - Leitura: O e-book `qa-e-book-27053706` é criado (201) e não abre na vitrine enquanto rascunho.
  - Evidências: `qa-harness/evidencias/api/administracao/06-cadastrar-ebook.json`, `qa-harness/evidencias/api/administracao/07-rascunho-na-vitrine.json`
- **Ponto 5 - Arquivo exe é recusado como e-book** — **VALIDO**
  - História: História 2 - Administrador cadastra e publica um e-book
  - Leitura: O `.exe` é recusado: 422 "Formato não suportado: .exe. Use pdf, epub ou txt.".
  - Evidências: `qa-harness/evidencias/api/administracao/08-upload-exe.json`
- **Ponto 6 - Publicar põe o e-book na vitrine** — **VALIDO**
  - História: História 2 - Administrador cadastra e publica um e-book
  - Leitura: Depois de publicado, `qa-e-book-27053706` aparece no catálogo público.
  - Evidências: `qa-harness/evidencias/api/administracao/09-publicar-ebook.json`, `qa-harness/evidencias/api/administracao/10-catalogo-depois-de-publicar.json`
- **Ponto 7 - Lista de pedidos traz status, valor e data** — **VALIDO**
  - História: História 3 - Administrador acompanha as vendas
  - Leitura: Cada pedido da lista traz status, valor e data.
  - Evidências: `qa-harness/evidencias/api/administracao/11-lista-de-pedidos.json`
- **Ponto 8 - Detalhe do pedido traz itens e status** — **VALIDO**
  - História: História 3 - Administrador acompanha as vendas
  - Leitura: O detalhe traz o pedido pago de 99.80 com os 2 itens.
  - Evidências: `qa-harness/evidencias/api/administracao/12-detalhe-do-pedido.json`
- **Ponto 9 - Relatório de vendas do período soma os pedidos pagos** — **VALIDO**
  - História: História 3 - Administrador acompanha as vendas
  - Leitura: O relatório do período conta 3 pedido(s) pago(s), receita 189.6.
  - Evidências: `qa-harness/evidencias/api/administracao/13-relatorio-de-vendas.json`
- **Ponto 10 - Avaliação pendente está na fila de moderação** — **VALIDO**
  - História: História 4 - Administrador modera as avaliações
  - Leitura: A fila de moderação contém a avaliação `qa-avaliacao-pendente`.
  - Evidências: `qa-harness/evidencias/api/administracao/14-fila-de-moderacao.json`
- **Ponto 11 - Aprovar publica a avaliação na página do e-book** — **VALIDO**
  - História: História 4 - Administrador modera as avaliações
  - Leitura: O comentário não aparece antes e aparece na lista pública depois da aprovação.
  - Evidências: `qa-harness/evidencias/api/administracao/15-fila-antes-de-aprovar.json`, `qa-harness/evidencias/api/administracao/16-avaliacoes-publicas-antes.json`, `qa-harness/evidencias/api/administracao/17-aprovar-avaliacao.json`, `qa-harness/evidencias/api/administracao/18-avaliacoes-publicas-depois.json`
- **Ponto 12 - Cupom criado passa a valer** — **VALIDO**
  - História: História 5 - Administrador gerencia cupons de desconto
  - Leitura: O cupom `QA-27053706` é criado e vale: 39.90 → 31.92.
  - Evidências: `qa-harness/evidencias/api/administracao/19-criar-cupom.json`, `qa-harness/evidencias/api/administracao/20-validar-cupom-criado.json`
- **Ponto 13 - Cupom desativado deixa de valer** — **VALIDO**
  - História: História 5 - Administrador gerencia cupons de desconto
  - Leitura: Desativado, o cupom é recusado na validação (422).
  - Evidências: `qa-harness/evidencias/api/administracao/21-desativar-cupom.json`, `qa-harness/evidencias/api/administracao/22-validar-cupom-desativado.json`
### Domínio biblioteca

- **Ponto 1 - Biblioteca do comprador traz os e-books pagos** — **VALIDO**
  - História: História 1 - Comprador baixa um e-book da biblioteca
  - Leitura: A biblioteca do cliente traz `python-na-pratica` e `arquitetura-limpa-web`.
  - Evidências: `qa-harness/evidencias/api/biblioteca/01-biblioteca-cliente.json`
- **Ponto 2 - Biblioteca de quem não comprou está vazia** — **VALIDO**
  - História: História 1 - Comprador baixa um e-book da biblioteca
  - Leitura: A biblioteca de `sem_compras` é uma lista vazia.
  - Evidências: `qa-harness/evidencias/api/biblioteca/02-biblioteca-sem-compras.json`
- **Ponto 3 - Link válido entrega o arquivo sem expor o caminho** — **VALIDO**
  - História: História 1 - Comprador baixa um e-book da biblioteca
  - Leitura: O link válido entrega o arquivo como anexo, com o texto do e-book e sem caminho do servidor.
  - Evidências: `qa-harness/evidencias/api/biblioteca/03-download-valido.json`
- **Ponto 4 - Link expirado é negado** — **VALIDO**
  - História: História 1 - Comprador baixa um e-book da biblioteca
  - Leitura: O link responde 410 "Link de download expirado" sem arquivo.
  - Evidências: `qa-harness/evidencias/api/biblioteca/04-download-expirado.json`
- **Ponto 5 - Link que atingiu o limite é negado** — **VALIDO**
  - História: História 1 - Comprador baixa um e-book da biblioteca
  - Leitura: O link responde 429 "Limite de downloads atingido" sem arquivo.
  - Evidências: `qa-harness/evidencias/api/biblioteca/05-download-esgotado.json`
- **Ponto 6 - Quem não possui o e-book não gera link** — **VALIDO**
  - História: História 1 - Comprador baixa um e-book da biblioteca
  - Leitura: Quem não possui recebe 403; o dono recebe um link de download.
  - Evidências: `qa-harness/evidencias/api/biblioteca/06-link-de-quem-nao-possui.json`, `qa-harness/evidencias/api/biblioteca/07-link-do-dono.json`
- **Ponto 7 - Favorito entra na lista de favoritos** — **VALIDO**
  - História: História 2 - Comprador guarda e-books nos favoritos
  - Leitura: Depois de favoritar (204), `fastapi-do-zero` está nos favoritos.
  - Evidências: `qa-harness/evidencias/api/biblioteca/08-favoritar.json`, `qa-harness/evidencias/api/biblioteca/09-favoritos.json`
- **Ponto 8 - Comprador verificado envia avaliação** — **VALIDO**
  - História: História 3 - Comprador avalia um e-book que comprou
  - Leitura: A avaliação do dono é criada (201) com o comentário enviado.
  - Evidências: `qa-harness/evidencias/api/biblioteca/10-avaliacao-do-dono.json`
- **Ponto 9 - Quem não comprou não avalia** — **VALIDO**
  - História: História 3 - Comprador avalia um e-book que comprou
  - Leitura: Sem posse, a avaliação responde 403 "Só quem comprou pode avaliar".
  - Evidências: `qa-harness/evidencias/api/biblioteca/11-avaliacao-sem-posse.json`
- **Ponto 10 - Avaliação pendente não aparece para o público** — **VALIDO**
  - História: História 3 - Comprador avalia um e-book que comprou
  - Leitura: A lista pública de avaliações não contém o comentário pendente.
  - Evidências: `qa-harness/evidencias/api/biblioteca/12-avaliacoes-publicas.json`
### Domínio compra

- **Ponto 1 - Carrinho recebe o e-book e mostra o preço** — **VALIDO**
  - História: História 1 - Comprador compra pelo carrinho e paga
  - Leitura: O carrinho lista `fastapi-do-zero` a 49.90 depois da adição (204).
  - Evidências: `qa-harness/evidencias/api/compra/01-carrinho-adicionar.json`, `qa-harness/evidencias/api/compra/02-carrinho-listar.json`
- **Ponto 2 - Finalizar o carrinho cria pedido pendente com link de pagamento** — **VALIDO**
  - História: História 1 - Comprador compra pelo carrinho e paga
  - Leitura: O checkout cria o pedido pendente de 49.90 com referência própria.
  - Evidências: `qa-harness/evidencias/api/compra/03-carrinho-finalizar.json`
- **Ponto 3 - Aprovar no simulador deixa o pedido pago com download** — **VALIDO**
  - História: História 1 - Comprador compra pelo carrinho e paga
  - Leitura: O confirm redireciona para o pedido, que mostra "✓ Pago" e "Baixar".
  - Evidências: `qa-harness/evidencias/api/compra/04-carrinho-simulador.json`, `qa-harness/evidencias/api/compra/05-carrinho-aprovar.json`, `qa-harness/evidencias/api/compra/06-carrinho-pedido-pago.json`
- **Ponto 4 - Páginas de pagamento recebem o visual da loja** — **VALIDO**
  - História: História 1 - Comprador compra pelo carrinho e paga
  - Leitura: A folha de estilo do simulador e do pedido chega como `text/css`.
  - Evidências: `qa-harness/evidencias/api/compra/07-estilo-das-paginas-de-pagamento.json`
- **Ponto 5 - E-book pago entra na biblioteca do comprador** — **VALIDO**
  - História: História 1 - Comprador compra pelo carrinho e paga
  - Leitura: A biblioteca do cliente passa a conter `fastapi-do-zero`.
  - Evidências: `qa-harness/evidencias/api/compra/08-biblioteca-depois-de-pago.json`
- **Ponto 6 - Convidado cria pedido pendente com link de pagamento** — **VALIDO**
  - História: História 2 - Visitante compra um e-book sem ter conta
  - Leitura: O pedido de convidado nasce pendente com `checkout_url` para o simulador.
  - Evidências: `qa-harness/evidencias/api/compra/09-pedido-convidado.json`
- **Ponto 7 - Cupom válido calcula o total com desconto** — **VALIDO**
  - História: História 3 - Comprador usa um cupom de desconto
  - Leitura: BEMVINDO10 sobre 39.90 é válido com total 35.91.
  - Evidências: `qa-harness/evidencias/api/compra/10-cupom-valido.json`
- **Ponto 8 - Cupom inexistente é recusado** — **VALIDO**
  - História: História 3 - Comprador usa um cupom de desconto
  - Leitura: Cupom inexistente responde 422 "Cupom inválido".
  - Evidências: `qa-harness/evidencias/api/compra/11-cupom-inexistente.json`
- **Ponto 9 - Pedido com cupom é gravado com o desconto** — **VALIDO**
  - História: História 3 - Comprador usa um cupom de desconto
  - Leitura: O pedido com BEMVINDO10 é gravado com `amount` 35.91.
  - Evidências: `qa-harness/evidencias/api/compra/12-pedido-com-cupom.json`
- **Ponto 10 - Cupom digitado em minúsculas vale no pedido como vale na prévia** — **VALIDO**
  - História: História 3 - Comprador usa um cupom de desconto
  - Leitura: Digitado em minúsculas, o cupom vale no pedido como vale na prévia (35.91).
  - Evidências: `qa-harness/evidencias/api/compra/13-cupom-previa-da-tela.json`, `qa-harness/evidencias/api/compra/14-pedido-cupom-minusculo.json`
- **Ponto 11 - Pedido pendente em Meus pedidos traz como pagar** — **VALIDO**
  - História: História 4 - Comprador acompanha os pedidos e retoma um pagamento pendente
  - Leitura: O pedido pendente aparece com status, valor e `checkout_url` para pagar.
  - Evidências: `qa-harness/evidencias/api/compra/15-pedido-pendente-da-conta.json`, `qa-harness/evidencias/api/compra/16-meus-pedidos.json`
- **Ponto 12 - Webhook aprovado paga o pedido** — **VALIDO**
  - História: História 5 - Sistema confirma o pagamento pelo webhook
  - Leitura: O webhook é aplicado e a página do pedido mostra "✓ Pago" com "Baixar".
  - Evidências: `qa-harness/evidencias/api/compra/17-webhook-aprovado.json`, `qa-harness/evidencias/api/compra/18-webhook-pedido-pago.json`
- **Ponto 13 - Webhook repetido não repete efeito** — **VALIDO**
  - História: História 5 - Sistema confirma o pagamento pelo webhook
  - Leitura: A repetição volta ALREADY_PROCESSED e o pedido mantém 1 link(s) de download.
  - Evidências: `qa-harness/evidencias/api/compra/19-webhook-repetido.json`, `qa-harness/evidencias/api/compra/20-webhook-pedido-depois-da-repeticao.json`
- **Ponto 14 - Pedido pendente não libera download** — **VALIDO**
  - História: História 5 - Sistema confirma o pagamento pelo webhook
  - Leitura: O pedido pendente mostra "Aguardando" e nenhum link de download.
  - Evidências: `qa-harness/evidencias/api/compra/21-pedido-pendente-convidado.json`, `qa-harness/evidencias/api/compra/22-pedido-pendente-pagina.json`
### Domínio vitrine

- **Ponto 1 - Catálogo público lista os três publicados sem o rascunho** — **VALIDO**
  - História: História 1 - Visitante conhece a loja e o catálogo
  - Leitura: O catálogo lista exatamente os 3 publicados, cada um com título, autor e preço, e não mostra o rascunho.
  - Evidências: `qa-harness/evidencias/api/vitrine/01-catalogo-publico.json`
- **Ponto 2 - Rascunho não abre pelo endereço direto** — **VALIDO**
  - História: História 1 - Visitante conhece a loja e o catálogo
  - Leitura: O endereço direto do rascunho responde 404: ele não existe para a vitrine.
  - Evidências: `qa-harness/evidencias/api/vitrine/02-rascunho-direto.json`
- **Ponto 3 - Busca por FastAPI traz só o e-book certo** — **VALIDO**
  - História: História 2 - Visitante busca um e-book por título ou autor
  - Leitura: A busca por FastAPI traz `fastapi-do-zero` e não traz `python-na-pratica`.
  - Evidências: `qa-harness/evidencias/api/vitrine/03-busca-fastapi.json`
- **Ponto 4 - Filtro a partir de 50 reais traz só o e-book mais caro** — **VALIDO**
  - História: História 3 - Visitante filtra e ordena o catálogo por preço
  - Leitura: Com `price_min=50` só vem `arquitetura-limpa-web` (R$ 59,90).
  - Evidências: `qa-harness/evidencias/api/vitrine/04-filtro-preco-50.json`
- **Ponto 5 - Ordenação por menor preço começa pelo mais barato** — **VALIDO**
  - História: História 3 - Visitante filtra e ordena o catálogo por preço
  - Leitura: A lista começa por `python-na-pratica` (39,90) e os preços vêm em ordem crescente.
  - Evidências: `qa-harness/evidencias/api/vitrine/05-ordenacao-menor-preco.json`
- **Ponto 6 - Detalhe traz título, autor, descrição e preço** — **VALIDO**
  - História: História 4 - Visitante vê o detalhe de um e-book
  - Leitura: O detalhe traz título, autor, descrição e preço 39.90 de `python-na-pratica`.
  - Evidências: `qa-harness/evidencias/api/vitrine/06-detalhe-python.json`
- **Ponto 7 - Newsletter aceita a inscrição e a repetição sem duplicar** — **VALIDO**
  - História: História 5 - Visitante assina a newsletter
  - Leitura: As duas inscrições do mesmo e-mail respondem sucesso com `status` subscribed.
  - Evidências: `qa-harness/evidencias/api/vitrine/07-newsletter-primeira.json`, `qa-harness/evidencias/api/vitrine/08-newsletter-repetida.json`
- **Ponto 8 - Endereço da política de privacidade entrega a política** — **VALIDO**
  - História: História 6 - Visitante lê a política de privacidade e os termos
  - Leitura: O endereço `/privacidade` entrega a página com o título "Política de Privacidade".
  - Evidências: `qa-harness/evidencias/api/vitrine/09-privacidade.json`
- **Ponto 9 - Endereço dos termos de uso entrega os termos** — **VALIDO**
  - História: História 6 - Visitante lê a política de privacidade e os termos
  - Leitura: O endereço `/termos` entrega a página com o título "Termos de Uso".
  - Evidências: `qa-harness/evidencias/api/vitrine/10-termos.json`

## Ajuste/retorno para o desenvolvimento

Nenhuma falha de produto nesta execução.

## Lacunas de especificação (lint das histórias)

Nenhuma: toda jornada cita história existente, verifica o resultado e marca INICIO e FIM.

## Revisão de validade e healing

Execução de healing (ciclo 1) da rodada 2 — só integração, mesmo build do produto. O ponto 6 de acesso passou a enviar o corpo atual da tela (`person_type` individual) e responde 200. Os demais 52 pontos repetem o resultado da rodada 2. Vereditos consolidados em 2026-09-27-0521.

Todos os vereditos automáticos se confirmaram na leitura das evidências.

## Criados nesta execução

Nada criado — execução sobre artefatos existentes.

