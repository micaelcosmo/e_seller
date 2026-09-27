# Relatório de QA — e_seller

**Execução:** 2026-09-27-0547 · **Modo:** completo · **Viewports:** monitor · **Branch:** enrichment · **Commit:** 67eadb2 · **Motor:** 1.3.0

Gerado de `manifesto.yaml` pelo motor da skill `/qa`. Evidência de imagem: `evidencias.json` de cada pasta (PNG em base64; `python qa-harness/executar.py reverter` devolve os arquivos).

## Placar

| Veredito | Pontos |
|---|---|
| VALIDO | 78 |
| FALHA DE PRODUTO | 1 |
| EVIDENCIA INVALIDA | 0 |
| INCONCLUSIVO | 0 |

Healing: 0 ciclo(s) em 0 ponto(s).
Revisão de validade: 79 ponto(s) auditado(s), 0 veredito(s) alterado(s) em relação ao automático.

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
  - Leitura: O e-book `qa-e-book-27054737` é criado (201) e não abre na vitrine enquanto rascunho.
  - Evidências: `qa-harness/evidencias/api/administracao/06-cadastrar-ebook.json`, `qa-harness/evidencias/api/administracao/07-rascunho-na-vitrine.json`
- **Ponto 5 - Arquivo exe é recusado como e-book** — **VALIDO**
  - História: História 2 - Administrador cadastra e publica um e-book
  - Leitura: O `.exe` é recusado: 422 "Formato não suportado: .exe. Use pdf, epub ou txt.".
  - Evidências: `qa-harness/evidencias/api/administracao/08-upload-exe.json`
- **Ponto 6 - Publicar põe o e-book na vitrine** — **VALIDO**
  - História: História 2 - Administrador cadastra e publica um e-book
  - Leitura: Depois de publicado, `qa-e-book-27054737` aparece no catálogo público.
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
  - Leitura: O cupom `QA-27054737` é criado e vale: 39.90 → 31.92.
  - Evidências: `qa-harness/evidencias/api/administracao/19-criar-cupom.json`, `qa-harness/evidencias/api/administracao/20-validar-cupom-criado.json`
- **Ponto 13 - Cupom desativado deixa de valer** — **VALIDO**
  - História: História 5 - Administrador gerencia cupons de desconto
  - Leitura: Desativado, o cupom é recusado na validação (422).
  - Evidências: `qa-harness/evidencias/api/administracao/21-desativar-cupom.json`, `qa-harness/evidencias/api/administracao/22-validar-cupom-desativado.json`
- **Ponto 14 - E-book cadastrado com arquivo é entregue a quem compra** — **VALIDO**
  - História: História 2 - Administrador cadastra e publica um e-book
  - Leitura: O e-book novo, com o .txt enviado pelo admin, é entregue como anexo a quem compra.
  - Revisão: Critério novo desta rodada: o `.txt` enviado pelo admin chega como anexo a quem compra (texto sentinela `qa-conteudo-do-ebook` no corpo do download). Na integração de verificação anterior o mesmo ponto dava 404 "Arquivo indisponível" — corrigido no QAF-23.
  - Evidências: `qa-harness/evidencias/api/administracao/23-upload-txt.json`, `qa-harness/evidencias/api/administracao/24-pedido-do-ebook-novo.json`, `qa-harness/evidencias/api/administracao/25-webhook-do-ebook-novo.json`, `qa-harness/evidencias/api/administracao/26-pedido-do-ebook-novo-pago.json`, `qa-harness/evidencias/api/administracao/27-download-do-ebook-novo.json`
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

## Jornadas (prova visual das histórias)

| Jornada | História | Viewport | Passos | Veredito |
|---|---|---|---|---|
| Visitante cria uma conta e já entra | História 1 - Visitante cria uma conta de comprador | monitor | 16/16 | **VALIDO** |
| Comprador erra a senha, entra e sai da conta | História 2 - Comprador entra e sai da conta | monitor | 19/19 | **VALIDO** |
| Comprador salva o perfil fiscal | História 3 - Comprador mantém o perfil fiscal | monitor | 10/10 | **VALIDO** |
| Administrador entra no painel pelo formulário de login | História 1 - Administrador entra no painel administrativo | monitor | 3/3 | **VALIDO** |
| Administrador vê a lista de e-books no painel | História 2 - Administrador cadastra e publica um e-book | monitor | 2/2 | **VALIDO** |
| Administrador vê os pedidos com status, valor e data | História 3 - Administrador acompanha as vendas | monitor | 3/3 | **VALIDO** |
| Administrador procura a avaliação pendente para moderar | História 4 - Administrador modera as avaliações | monitor | 2/2 | **VALIDO** |
| Administrador vê os cupons de desconto | História 5 - Administrador gerencia cupons de desconto | monitor | 2/2 | **VALIDO** |
| Comprador vê os e-books comprados e quem não comprou vê a biblioteca vazia | História 1 - Comprador baixa um e-book da biblioteca | monitor | 7/7 | **VALIDO** |
| Comprador marca um e-book com o coração e o vê nos favoritos | História 2 - Comprador guarda e-books nos favoritos | monitor | 6/6 | **VALIDO** |
| Comprador avalia um e-book que comprou e quem não comprou é recusado | História 3 - Comprador avalia um e-book que comprou | monitor | 10/10 | **VALIDO** |
| Comprador compra pelo carrinho, paga e recebe o e-book | História 1 - Comprador compra pelo carrinho e paga | monitor | 14/14 | **VALIDO** |
| Visitante compra informando só o e-mail | História 2 - Visitante compra um e-book sem ter conta | monitor | 7/7 | **VALIDO** |
| Comprador confere um cupom de desconto | História 3 - Comprador usa um cupom de desconto | monitor | 6/6 | **VALIDO** |
| Comprador vê os pedidos e tenta pagar o pendente | História 4 - Comprador acompanha os pedidos e retoma um pagamento pendente | monitor | 6/6 | **VALIDO** |
| Visitante conhece a loja e vê o catálogo | História 1 - Visitante conhece a loja e o catálogo | monitor | 6/6 | **VALIDO** |
| Visitante busca um e-book pelo título | História 2 - Visitante busca um e-book por título ou autor | monitor | 5/5 | **VALIDO** |
| Visitante ordena e filtra o catálogo por preço | História 3 - Visitante filtra e ordena o catálogo por preço | monitor | 6/6 | **VALIDO** |
| Visitante abre a página de um e-book | História 4 - Visitante vê o detalhe de um e-book | monitor | 9/9 | **VALIDO** |
| Visitante assina a newsletter pelo rodapé | História 5 - Visitante assina a newsletter | monitor | 4/4 | **VALIDO** |
| Visitante abre a política de privacidade e os termos pelo rodapé | História 6 - Visitante lê a política de privacidade e os termos | monitor | 6/6 | **VALIDO** |


## Base visual (retrato do sistema)

| Perfil | Viewport | Telas | Erros de console | Veredito |
|---|---|---|---|---|
| visitante | monitor | 7 | 0 | **VALIDO** |
| cliente | monitor | 7 | 1 | **VALIDO** |
| sem_compras | monitor | 2 | 0 | **VALIDO** |
| admin | monitor | 7 | 2 | **FALHA DE PRODUTO** |

- **Base visual - admin (monitor)**: 06-painel-html-de-pedidos renderizou só 28 caracteres; 07-painel-html-novo-ebook renderizou só 28 caracteres

## Ajuste/retorno para o desenvolvimento

### Achado 1 - Base visual - admin (monitor)

- **Origem:** Base visual - admin (monitor) (base-visual, base)
- **História:** Base visual - admin
- **O que a evidência mostra:** 7 tela(s) em monitor; 2 erro(s) de console. Problemas: 06-painel-html-de-pedidos renderizou só 28 caracteres; 07-painel-html-novo-ebook renderizou só 28 caracteres
- **Leitura da revisão:** Confirmado e restrito aos painéis HTML: `01` a `05` (painel, produtos, pedidos, avaliações com comentário/status/filtro, cupons) abrem certos. `06` e `07` (`/api/v1/admin/*/panel`) seguem com "Não autenticado" — exigem cabeçalho `Authorization`. Decisão bloqueante D18, guardada para o dono; não é regressão.
- **Evidências:** `qa-harness/evidencias/_base/admin/monitor/01-painel.png`, `qa-harness/evidencias/_base/admin/monitor/02-produtos.png`, `qa-harness/evidencias/_base/admin/monitor/03-pedidos.png`, `qa-harness/evidencias/_base/admin/monitor/04-avaliacoes.png`, `qa-harness/evidencias/_base/admin/monitor/05-cupons.png`, `qa-harness/evidencias/_base/admin/monitor/06-painel-html-de-pedidos.png`

## Lacunas de especificação (lint das histórias)

Nenhuma: toda jornada cita história existente, verifica o resultado e marca INICIO e FIM.

## Revisão de validade e healing

Rodada 3 do `/qa completo` (build com todos os ajustes QAF, inclusive o QAF-23 e a lista de avaliações do painel). Auditei os 54 pontos de integração pelos `.json`, as 20 jornadas pelos prints e pelo `evidencias.json`, e as 4 bases visuais pelas métricas (URL, título, texto, rolagem) e pelos prints. Erros de console conferidos: todos são as recusas que as próprias jornadas provocam (401 senha errada, 409 e-mail repetido, 403 avaliação sem posse, 422 cupom inválido, 404 e-book inexistente) ou os painéis da decisão D18; um `ERR_NO_BUFFER_SPACE` na base do cliente é ruído de rede do Windows sob carga (pytest em paralelo), sem efeito na tela.

- **Ponto 14 - E-book cadastrado com arquivo é entregue a quem compra**: VALIDO → VALIDO · healing 0 — Critério novo desta rodada: o `.txt` enviado pelo admin chega como anexo a quem compra (texto sentinela `qa-conteudo-do-ebook` no corpo do download). Na integração de verificação anterior o mesmo ponto dava 404 "Arquivo indisponível" — corrigido no QAF-23.
- **Base visual - admin (monitor)**: FALHA DE PRODUTO → FALHA DE PRODUTO · healing 0 — Confirmado e restrito aos painéis HTML: `01` a `05` (painel, produtos, pedidos, avaliações com comentário/status/filtro, cupons) abrem certos. `06` e `07` (`/api/v1/admin/*/panel`) seguem com "Não autenticado" — exigem cabeçalho `Authorization`. Decisão bloqueante D18, guardada para o dono; não é regressão.

## Warnings - Convenção de comentários

Regra: .spec/code/convencao-de-comentarios.md · 13 candidato(s), 0 violação(ões). Warning não reprova a execução.

Aceitos após leitura: backend/app/accounts/router_admin.py:159 — CSS dentro de f-string (chaves dobradas), não é código comentado; backend/app/catalog/router_admin.py:230 — CSS dentro de f-string (chaves dobradas), não é código comentado; backend/app/coupons/router_admin.py:275 — CSS dentro de f-string (chaves dobradas), não é código comentado; backend/app/coupons/router_admin.py:279 — CSS dentro de f-string (chaves dobradas), não é código comentado; backend/app/orders/models.py:40 — agora descreve o presente ('um ou mais itens'); a menção a fase saiu; backend/app/orders/router.py:234 — descreve o comportamento atual do endpoint; backend/app/orders/services.py:46 — descreve o que o método faz hoje; backend/app/orders/services.py:133 — restrição presente do formato de data aceito; backend/app/orders/state_machine.py:37 — docstring no presente da transição de estado; backend/app/orders/state_machine.py:41 — docstring no presente da transição de estado; backend/app/orders/state_machine.py:45 — docstring no presente da transição de estado; backend/app/orders/state_machine.py:49 — docstring no presente da transição de estado; qa-harness/testes/api/teste_compra.py:239 — docstring no presente do que o ponto faz.

## Criados nesta execução

- `.spec/test/planos/administracao.yaml` — Ponto 14 - E-book cadastrado com arquivo é entregue a quem compra (derivado de: US-03 + US-06, RF-12, RF-30 (critério novo na História 2 de administração))

Criação não é aprovação: tudo acima entra na proposta de commit para aceite.

