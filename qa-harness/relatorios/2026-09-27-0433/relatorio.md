# Relatório de QA — e_seller

**Execução:** 2026-09-27-0433 · **Modo:** completo · **Viewports:** monitor · **Branch:** enrichment · **Commit:** 67eadb2 · **Motor:** 1.3.0

Gerado de `manifesto.yaml` pelo motor da skill `/qa`. Evidência de imagem: `evidencias.json` de cada pasta (PNG em base64; `python qa-harness/executar.py reverter` devolve os arquivos).

## Placar

| Veredito | Pontos |
|---|---|
| VALIDO | 55 |
| FALHA DE PRODUTO | 23 |
| EVIDENCIA INVALIDA | 0 |
| INCONCLUSIVO | 0 |

Healing: 12 ciclo(s) em 12 ponto(s).
Revisão de validade: 78 ponto(s) auditado(s), 10 veredito(s) alterado(s) em relação ao automático.

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
- **Ponto 6 - Perfil fiscal enviado como a tela envia é salvo** — **FALHA DE PRODUTO**
  - História: História 3 - Comprador mantém o perfil fiscal
  - Leitura: ao corpo que a tela envia (`person_type` "PF") a API respondeu 422 {'detail': [{'type': 'enum', 'loc': ['body', 'person_type'], 'msg': "Input should be 'individual' or 'company'", 'input': 'PF', 'ctx': {'expected': "'individual' or 'company'"}}]}
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
- **Ponto 3 - Formulário de login do painel abre o painel** — **FALHA DE PRODUTO**
  - História: História 1 - Administrador entra no painel administrativo
  - Leitura: o envio do formulário de login do painel respondeu 403 "Token CSRF inválido." (destino ``)
  - Evidências: `qa-harness/evidencias/api/administracao/03-painel-formulario-de-login.json`, `qa-harness/evidencias/api/administracao/04-painel-enviar-login.json`
- **Ponto 4 - E-book novo nasce como rascunho fora da vitrine** — **VALIDO**
  - História: História 2 - Administrador cadastra e publica um e-book
  - Leitura: O e-book `qa-e-book-27043406` é criado (201) e não abre na vitrine enquanto rascunho.
  - Evidências: `qa-harness/evidencias/api/administracao/05-cadastrar-ebook.json`, `qa-harness/evidencias/api/administracao/06-rascunho-na-vitrine.json`
- **Ponto 5 - Arquivo exe é recusado como e-book** — **VALIDO**
  - História: História 2 - Administrador cadastra e publica um e-book
  - Leitura: O `.exe` é recusado: 422 "Formato não suportado: .exe. Use pdf, epub ou txt.".
  - Evidências: `qa-harness/evidencias/api/administracao/07-upload-exe.json`
- **Ponto 6 - Publicar põe o e-book na vitrine** — **VALIDO**
  - História: História 2 - Administrador cadastra e publica um e-book
  - Leitura: Depois de publicado, `qa-e-book-27043406` aparece no catálogo público.
  - Evidências: `qa-harness/evidencias/api/administracao/08-publicar-ebook.json`, `qa-harness/evidencias/api/administracao/09-catalogo-depois-de-publicar.json`
- **Ponto 7 - Lista de pedidos traz status, valor e data** — **FALHA DE PRODUTO**
  - História: História 3 - Administrador acompanha as vendas
  - Leitura: os pedidos da lista vêm sem created_at (campos: amount, checkout_url, reference, status)
  - Evidências: `qa-harness/evidencias/api/administracao/10-lista-de-pedidos.json`
- **Ponto 8 - Detalhe do pedido traz itens e status** — **VALIDO**
  - História: História 3 - Administrador acompanha as vendas
  - Leitura: O detalhe traz o pedido pago de 99.80 com os 2 itens.
  - Evidências: `qa-harness/evidencias/api/administracao/11-detalhe-do-pedido.json`
- **Ponto 9 - Relatório de vendas do período soma os pedidos pagos** — **VALIDO**
  - História: História 3 - Administrador acompanha as vendas
  - Leitura: O relatório do período conta 3 pedido(s) pago(s), receita 189.6.
  - Evidências: `qa-harness/evidencias/api/administracao/12-relatorio-de-vendas.json`
- **Ponto 10 - Avaliação pendente está na fila de moderação** — **VALIDO**
  - História: História 4 - Administrador modera as avaliações
  - Leitura: A fila de moderação contém a avaliação `qa-avaliacao-pendente`.
  - Evidências: `qa-harness/evidencias/api/administracao/13-fila-de-moderacao.json`
- **Ponto 11 - Aprovar publica a avaliação na página do e-book** — **VALIDO**
  - História: História 4 - Administrador modera as avaliações
  - Leitura: O comentário não aparece antes e aparece na lista pública depois da aprovação.
  - Evidências: `qa-harness/evidencias/api/administracao/14-fila-antes-de-aprovar.json`, `qa-harness/evidencias/api/administracao/15-avaliacoes-publicas-antes.json`, `qa-harness/evidencias/api/administracao/16-aprovar-avaliacao.json`, `qa-harness/evidencias/api/administracao/17-avaliacoes-publicas-depois.json`
- **Ponto 12 - Cupom criado passa a valer** — **VALIDO**
  - História: História 5 - Administrador gerencia cupons de desconto
  - Leitura: O cupom `QA-27043406` é criado e vale: 39.90 → 31.92.
  - Evidências: `qa-harness/evidencias/api/administracao/18-criar-cupom.json`, `qa-harness/evidencias/api/administracao/19-validar-cupom-criado.json`
- **Ponto 13 - Cupom desativado deixa de valer** — **VALIDO**
  - História: História 5 - Administrador gerencia cupons de desconto
  - Leitura: Desativado, o cupom é recusado na validação (422).
  - Evidências: `qa-harness/evidencias/api/administracao/20-desativar-cupom.json`, `qa-harness/evidencias/api/administracao/21-validar-cupom-desativado.json`
### Domínio biblioteca

- **Ponto 1 - Biblioteca do comprador traz os e-books pagos** — **VALIDO**
  - História: História 1 - Comprador baixa um e-book da biblioteca
  - Leitura: A biblioteca do cliente traz `python-na-pratica` e `arquitetura-limpa-web`.
  - Evidências: `qa-harness/evidencias/api/biblioteca/01-biblioteca-cliente.json`
- **Ponto 2 - Biblioteca de quem não comprou está vazia** — **VALIDO**
  - História: História 1 - Comprador baixa um e-book da biblioteca
  - Leitura: A biblioteca de `sem_compras` é uma lista vazia.
  - Evidências: `qa-harness/evidencias/api/biblioteca/02-biblioteca-sem-compras.json`
- **Ponto 3 - Link válido entrega o arquivo sem expor o caminho** — **FALHA DE PRODUTO**
  - História: História 1 - Comprador baixa um e-book da biblioteca
  - Leitura: download válido: status 500, disposição ``
  - Evidências: `qa-harness/evidencias/api/biblioteca/03-download-valido.json`
- **Ponto 4 - Link expirado é negado** — **FALHA DE PRODUTO**
  - História: História 1 - Comprador baixa um e-book da biblioteca
  - Leitura: esperava recusa ((410,), "expirado"); veio 500 Erro interno
  - Evidências: `qa-harness/evidencias/api/biblioteca/04-download-expirado.json`
- **Ponto 5 - Link que atingiu o limite é negado** — **FALHA DE PRODUTO**
  - História: História 1 - Comprador baixa um e-book da biblioteca
  - Leitura: esperava recusa ((403, 410, 429), "limite"); veio 500 Erro interno
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
- **Ponto 4 - Páginas de pagamento recebem o visual da loja** — **FALHA DE PRODUTO**
  - História: História 1 - Comprador compra pelo carrinho e paga
  - Leitura: `/static/css/design-system.css` pelo endereço da loja veio como `text/html` (status 200): simulador e pedido aparecem sem estilo
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
- **Ponto 10 - Cupom digitado em minúsculas vale no pedido como vale na prévia** — **FALHA DE PRODUTO**
  - História: História 3 - Comprador usa um cupom de desconto
  - Leitura: a prévia diz válido, mas o pedido com `bemvindo10` respondeu 422 {'type': 'https://e-seller.app/errors/422', 'title': 'Dados inválidos', 'status': 422, 'detail': 'Cupom inválido', 'instance': '/api/v1/orders'}
  - Evidências: `qa-harness/evidencias/api/compra/13-cupom-previa-da-tela.json`, `qa-harness/evidencias/api/compra/14-pedido-cupom-minusculo.json`
- **Ponto 11 - Pedido pendente em Meus pedidos traz como pagar** — **FALHA DE PRODUTO**
  - História: História 4 - Comprador acompanha os pedidos e retoma um pagamento pendente
  - Leitura: o pedido pendente aparece com `checkout_url` None: a tela não tem como oferecer "Pagar"
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
- **Ponto 3 - Busca por FastAPI traz só o e-book certo** — **FALHA DE PRODUTO**
  - História: História 2 - Visitante busca um e-book por título ou autor
  - Leitura: a busca `GET /api/v1/products?q=FastAPI` respondeu 500 (Erro interno)
  - Revisão: Confirmado: `GET /api/v1/products?q=FastAPI` responde 500 no Postgres (`SELECT DISTINCT` com `ORDER BY CASE` de relevância). O SPA não cai nisso porque sempre manda `sort` (sem relevância) — por isso a jornada de busca é válida — mas o contrato `?q=` sem `sort` quebra.
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
- **Ponto 8 - Endereço da política de privacidade entrega a política** — **FALHA DE PRODUTO**
  - História: História 6 - Visitante lê a política de privacidade e os termos
  - Leitura: `/privacidade` pelo endereço da loja não entrega "Política de Privacidade" (status 200; veio a página da loja)
  - Evidências: `qa-harness/evidencias/api/vitrine/09-privacidade.json`
- **Ponto 9 - Endereço dos termos de uso entrega os termos** — **FALHA DE PRODUTO**
  - História: História 6 - Visitante lê a política de privacidade e os termos
  - Leitura: `/termos` pelo endereço da loja não entrega "Termos de Uso" (status 200; veio a página da loja)
  - Evidências: `qa-harness/evidencias/api/vitrine/10-termos.json`

## Jornadas (prova visual das histórias)

| Jornada | História | Viewport | Passos | Veredito |
|---|---|---|---|---|
| Visitante cria uma conta e já entra | História 1 - Visitante cria uma conta de comprador | monitor | 16/16 | **VALIDO** |
| Comprador erra a senha, entra e sai da conta | História 2 - Comprador entra e sai da conta | monitor | 19/19 | **VALIDO** |
| Comprador salva o perfil fiscal | História 3 - Comprador mantém o perfil fiscal | monitor | 2/10 | **FALHA DE PRODUTO** |
| Administrador entra no painel pelo formulário de login | História 1 - Administrador entra no painel administrativo | monitor | 1/3 | **FALHA DE PRODUTO** (motor: EVIDENCIA INVALIDA) |
| Administrador vê a lista de e-books no painel | História 2 - Administrador cadastra e publica um e-book | monitor | 1/2 | **FALHA DE PRODUTO** (motor: EVIDENCIA INVALIDA) |
| Administrador vê os pedidos com status, valor e data | História 3 - Administrador acompanha as vendas | monitor | 1/3 | **FALHA DE PRODUTO** (motor: EVIDENCIA INVALIDA) |
| Administrador procura a avaliação pendente para moderar | História 4 - Administrador modera as avaliações | monitor | 1/2 | **FALHA DE PRODUTO** (motor: EVIDENCIA INVALIDA) |
| Administrador vê os cupons de desconto | História 5 - Administrador gerencia cupons de desconto | monitor | 1/2 | **FALHA DE PRODUTO** (motor: EVIDENCIA INVALIDA) |
| Comprador vê os e-books comprados e quem não comprou vê a biblioteca vazia | História 1 - Comprador baixa um e-book da biblioteca | monitor | 2/7 | **VALIDO** (motor: EVIDENCIA INVALIDA) |
| Comprador marca um e-book com o coração e o vê nos favoritos | História 2 - Comprador guarda e-books nos favoritos | monitor | 4/6 | **VALIDO** (motor: EVIDENCIA INVALIDA) |
| Comprador avalia um e-book que comprou e quem não comprou é recusado | História 3 - Comprador avalia um e-book que comprou | monitor | 10/10 | **VALIDO** |
| Comprador compra pelo carrinho, paga e recebe o e-book | História 1 - Comprador compra pelo carrinho e paga | monitor | 3/14 | **VALIDO** (motor: EVIDENCIA INVALIDA) |
| Visitante compra informando só o e-mail | História 2 - Visitante compra um e-book sem ter conta | monitor | 6/7 | **FALHA DE PRODUTO** |
| Comprador confere um cupom de desconto | História 3 - Comprador usa um cupom de desconto | monitor | 6/6 | **VALIDO** |
| Comprador vê os pedidos e tenta pagar o pendente | História 4 - Comprador acompanha os pedidos e retoma um pagamento pendente | monitor | 2/6 | **FALHA DE PRODUTO** (motor: EVIDENCIA INVALIDA) |
| Visitante conhece a loja e vê o catálogo | História 1 - Visitante conhece a loja e o catálogo | monitor | 6/6 | **VALIDO** |
| Visitante busca um e-book pelo título | História 2 - Visitante busca um e-book por título ou autor | monitor | 5/5 | **VALIDO** |
| Visitante ordena e filtra o catálogo por preço | História 3 - Visitante filtra e ordena o catálogo por preço | monitor | 6/6 | **VALIDO** |
| Visitante abre a página de um e-book | História 4 - Visitante vê o detalhe de um e-book | monitor | 9/9 | **VALIDO** |
| Visitante assina a newsletter pelo rodapé | História 5 - Visitante assina a newsletter | monitor | 4/4 | **VALIDO** |
| Visitante abre a política de privacidade e os termos pelo rodapé | História 6 - Visitante lê a política de privacidade e os termos | monitor | 3/6 | **FALHA DE PRODUTO** |

- **Jornada - Comprador salva o perfil fiscal**: 2/10 passos; 1 erro(s) de console. passo 2 (Vê o formulário do perfil fiscal): não achei "Minha Conta" em body
  - Revisão: Na rodada parou cedo pelo defeito do adaptador; no healing percorreu os 10 passos e o toast "Perfil salvo" não aparece: a API responde 422 (`person_type` "PF" — a API espera `individual`/`company`), igual ao Ponto 6 de acesso.
- **Jornada - Administrador entra no painel pelo formulário de login**: 1/3 passos; 13 erro(s) de console. passo 1 (Abre o painel administrativo): não consegui abrir /admin/: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/
  - Revisão: Automático EVIDENCIA INVALIDA (navegação recusada), mas a causa é o produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx). Repetiu igual no healing.
- **Jornada - Administrador vê a lista de e-books no painel**: 1/2 passos; 13 erro(s) de console. passo 1 (Abre a lista de produtos): não consegui abrir /admin/product/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/product/list
  - Revisão: Mesma causa do login do painel (CSRF + `Host` sem porta); a lista nunca abre.
- **Jornada - Administrador vê os pedidos com status, valor e data**: 1/3 passos; 13 erro(s) de console. passo 1 (Abre a lista de pedidos): não consegui abrir /admin/order/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/order/list
  - Revisão: Mesma causa do login do painel (CSRF + `Host` sem porta); a lista nunca abre.
- **Jornada - Administrador procura a avaliação pendente para moderar**: 1/2 passos; 13 erro(s) de console. passo 1 (Abre a lista de avaliações): não consegui abrir /admin/review/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/review/list
  - Revisão: Mesma causa do login do painel. Além disso, o código mostra que a lista de avaliações do painel não tem comentário nem status (`ReviewAdmin.column_list`) e não permite editar: moderar pela tela seria às cegas.
- **Jornada - Administrador vê os cupons de desconto**: 1/2 passos; 13 erro(s) de console. passo 1 (Abre a lista de cupons): não consegui abrir /admin/coupon/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/coupon/list
  - Revisão: Mesma causa do login do painel (CSRF + `Host` sem porta); a lista nunca abre.
- **Jornada - Comprador vê os e-books comprados e quem não comprou vê a biblioteca vazia**: 2/7 passos. passo 2 (Clica em Biblioteca): não consegui clicar: Locator.click: Timeout 20000ms exceeded.
  - Revisão: Botão Biblioteca escondido pelo defeito do adaptador; no healing os 7 passos passam (cliente com os e-books, `sem_compras` com a biblioteca vazia).
- **Jornada - Comprador marca um e-book com o coração e o vê nos favoritos**: 4/6 passos; 1 erro(s) de console. passo 4 (Clica em Favoritos): não consegui clicar: Locator.click: Timeout 20000ms exceeded.
  - Revisão: Válida no healing (coração marcado, e-book em "Meus favoritos"). O console registrou um 500 em `POST /api/v1/wishlist/fastapi-do-zero`: o clique dispara dois pedidos (o SPA liga o botão duas vezes) e o segundo estoura a UNIQUE no Postgres — achado de produto registrado à parte (QAF-16).
- **Jornada - Comprador compra pelo carrinho, paga e recebe o e-book**: 3/14 passos. passo 3 (Abre o carrinho): não consegui clicar: Locator.click: Timeout 20000ms exceeded.
  - Revisão: Válida no healing (14/14: carrinho 49,90, simulador, pedido pago com "Baixar", e-book na biblioteca). Os prints do simulador e do pedido mostram HTML sem estilo (o CSS de `/static/` volta como a página do SPA), o que já é a falha do Ponto 4 de compra.
- **Jornada - Visitante compra informando só o e-mail**: 6/7 passos. passo 6 (Chega à página de pagamento do pedido): a URL é http://127.0.0.1:48273/#/pedidos, esperava /pay/simulate/
- **Jornada - Comprador vê os pedidos e tenta pagar o pendente**: 2/6 passos. passo 2 (Clica em Pedidos): não consegui clicar: Locator.click: Timeout 20000ms exceeded.
  - Revisão: Chega aos pedidos no healing; o pedido pendente aparece sem "Pagar" (`checkout_url` nulo em `/orders/my`) — RF-25.
- **Jornada - Visitante busca um e-book pelo título**: 5/5 passos, do início ao fim, com todas as conferências confirmadas na tela.
  - Revisão: Print do passo 4 mostra só "FastAPI do Zero" com a busca preenchida; o SPA envia `sort=newest` e escapa do erro do Ponto 3.
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

### Achado 1 - Perfil fiscal enviado como a tela envia é salvo

- **Origem:** Ponto 6 - Perfil fiscal enviado como a tela envia é salvo (acesso, integracao)
- **História:** História 3 - Comprador mantém o perfil fiscal
- **O que a evidência mostra:** ao corpo que a tela envia (`person_type` "PF") a API respondeu 422 {'detail': [{'type': 'enum', 'loc': ['body', 'person_type'], 'msg': "Input should be 'individual' or 'company'", 'input': 'PF', 'ctx': {'expected': "'individual' or 'company'"}}]}
- **Evidências:** `qa-harness/evidencias/api/acesso/08-perfil-fiscal-da-tela.json`

### Achado 2 - Formulário de login do painel abre o painel

- **Origem:** Ponto 3 - Formulário de login do painel abre o painel (administracao, integracao)
- **História:** História 1 - Administrador entra no painel administrativo
- **O que a evidência mostra:** o envio do formulário de login do painel respondeu 403 "Token CSRF inválido." (destino ``)
- **Evidências:** `qa-harness/evidencias/api/administracao/03-painel-formulario-de-login.json`, `qa-harness/evidencias/api/administracao/04-painel-enviar-login.json`

### Achado 3 - Lista de pedidos traz status, valor e data

- **Origem:** Ponto 7 - Lista de pedidos traz status, valor e data (administracao, integracao)
- **História:** História 3 - Administrador acompanha as vendas
- **O que a evidência mostra:** os pedidos da lista vêm sem created_at (campos: amount, checkout_url, reference, status)
- **Evidências:** `qa-harness/evidencias/api/administracao/10-lista-de-pedidos.json`

### Achado 4 - Link válido entrega o arquivo sem expor o caminho

- **Origem:** Ponto 3 - Link válido entrega o arquivo sem expor o caminho (biblioteca, integracao)
- **História:** História 1 - Comprador baixa um e-book da biblioteca
- **O que a evidência mostra:** download válido: status 500, disposição ``
- **Evidências:** `qa-harness/evidencias/api/biblioteca/03-download-valido.json`

### Achado 5 - Link expirado é negado

- **Origem:** Ponto 4 - Link expirado é negado (biblioteca, integracao)
- **História:** História 1 - Comprador baixa um e-book da biblioteca
- **O que a evidência mostra:** esperava recusa ((410,), "expirado"); veio 500 Erro interno
- **Evidências:** `qa-harness/evidencias/api/biblioteca/04-download-expirado.json`

### Achado 6 - Link que atingiu o limite é negado

- **Origem:** Ponto 5 - Link que atingiu o limite é negado (biblioteca, integracao)
- **História:** História 1 - Comprador baixa um e-book da biblioteca
- **O que a evidência mostra:** esperava recusa ((403, 410, 429), "limite"); veio 500 Erro interno
- **Evidências:** `qa-harness/evidencias/api/biblioteca/05-download-esgotado.json`

### Achado 7 - Páginas de pagamento recebem o visual da loja

- **Origem:** Ponto 4 - Páginas de pagamento recebem o visual da loja (compra, integracao)
- **História:** História 1 - Comprador compra pelo carrinho e paga
- **O que a evidência mostra:** `/static/css/design-system.css` pelo endereço da loja veio como `text/html` (status 200): simulador e pedido aparecem sem estilo
- **Evidências:** `qa-harness/evidencias/api/compra/07-estilo-das-paginas-de-pagamento.json`

### Achado 8 - Cupom digitado em minúsculas vale no pedido como vale na prévia

- **Origem:** Ponto 10 - Cupom digitado em minúsculas vale no pedido como vale na prévia (compra, integracao)
- **História:** História 3 - Comprador usa um cupom de desconto
- **O que a evidência mostra:** a prévia diz válido, mas o pedido com `bemvindo10` respondeu 422 {'type': 'https://e-seller.app/errors/422', 'title': 'Dados inválidos', 'status': 422, 'detail': 'Cupom inválido', 'instance': '/api/v1/orders'}
- **Evidências:** `qa-harness/evidencias/api/compra/13-cupom-previa-da-tela.json`, `qa-harness/evidencias/api/compra/14-pedido-cupom-minusculo.json`

### Achado 9 - Pedido pendente em Meus pedidos traz como pagar

- **Origem:** Ponto 11 - Pedido pendente em Meus pedidos traz como pagar (compra, integracao)
- **História:** História 4 - Comprador acompanha os pedidos e retoma um pagamento pendente
- **O que a evidência mostra:** o pedido pendente aparece com `checkout_url` None: a tela não tem como oferecer "Pagar"
- **Evidências:** `qa-harness/evidencias/api/compra/15-pedido-pendente-da-conta.json`, `qa-harness/evidencias/api/compra/16-meus-pedidos.json`

### Achado 10 - Busca por FastAPI traz só o e-book certo

- **Origem:** Ponto 3 - Busca por FastAPI traz só o e-book certo (vitrine, integracao)
- **História:** História 2 - Visitante busca um e-book por título ou autor
- **O que a evidência mostra:** a busca `GET /api/v1/products?q=FastAPI` respondeu 500 (Erro interno)
- **Leitura da revisão:** Confirmado: `GET /api/v1/products?q=FastAPI` responde 500 no Postgres (`SELECT DISTINCT` com `ORDER BY CASE` de relevância). O SPA não cai nisso porque sempre manda `sort` (sem relevância) — por isso a jornada de busca é válida — mas o contrato `?q=` sem `sort` quebra.
- **Evidências:** `qa-harness/evidencias/api/vitrine/03-busca-fastapi.json`

### Achado 11 - Endereço da política de privacidade entrega a política

- **Origem:** Ponto 8 - Endereço da política de privacidade entrega a política (vitrine, integracao)
- **História:** História 6 - Visitante lê a política de privacidade e os termos
- **O que a evidência mostra:** `/privacidade` pelo endereço da loja não entrega "Política de Privacidade" (status 200; veio a página da loja)
- **Evidências:** `qa-harness/evidencias/api/vitrine/09-privacidade.json`

### Achado 12 - Endereço dos termos de uso entrega os termos

- **Origem:** Ponto 9 - Endereço dos termos de uso entrega os termos (vitrine, integracao)
- **História:** História 6 - Visitante lê a política de privacidade e os termos
- **O que a evidência mostra:** `/termos` pelo endereço da loja não entrega "Termos de Uso" (status 200; veio a página da loja)
- **Evidências:** `qa-harness/evidencias/api/vitrine/10-termos.json`

### Achado 13 - Comprador salva o perfil fiscal

- **Origem:** Jornada - Comprador salva o perfil fiscal (acesso, jornada)
- **História:** História 3 - Comprador mantém o perfil fiscal
- **O que a evidência mostra:** 2/10 passos; 1 erro(s) de console. passo 2 (Vê o formulário do perfil fiscal): não achei "Minha Conta" em body
- **Leitura da revisão:** Na rodada parou cedo pelo defeito do adaptador; no healing percorreu os 10 passos e o toast "Perfil salvo" não aparece: a API responde 422 (`person_type` "PF" — a API espera `individual`/`company`), igual ao Ponto 6 de acesso.
- **Evidências:** `qa-harness/evidencias/jornadas/acesso/comprador-salva-perfil-fiscal/monitor/01-abre-minha-conta.png`, `qa-harness/evidencias/jornadas/acesso/comprador-salva-perfil-fiscal/monitor/02-ve-o-formulario-do-perfil-fiscal.png`

### Achado 14 - Administrador entra no painel pelo formulário de login

- **Origem:** Jornada - Administrador entra no painel pelo formulário de login (administracao, jornada)
- **História:** História 1 - Administrador entra no painel administrativo
- **O que a evidência mostra:** 1/3 passos; 13 erro(s) de console. passo 1 (Abre o painel administrativo): não consegui abrir /admin/: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/
- **Leitura da revisão:** Automático EVIDENCIA INVALIDA (navegação recusada), mas a causa é o produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx). Repetiu igual no healing.
- **Evidências:** `qa-harness/evidencias/jornadas/administracao/administrador-entra-no-painel/monitor/01-abre-o-painel-administrativo.png`

### Achado 15 - Administrador vê a lista de e-books no painel

- **Origem:** Jornada - Administrador vê a lista de e-books no painel (administracao, jornada)
- **História:** História 2 - Administrador cadastra e publica um e-book
- **O que a evidência mostra:** 1/2 passos; 13 erro(s) de console. passo 1 (Abre a lista de produtos): não consegui abrir /admin/product/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/product/list
- **Leitura da revisão:** Mesma causa do login do painel (CSRF + `Host` sem porta); a lista nunca abre.
- **Evidências:** `qa-harness/evidencias/jornadas/administracao/administrador-ve-os-produtos/monitor/01-abre-a-lista-de-produtos.png`

### Achado 16 - Administrador vê os pedidos com status, valor e data

- **Origem:** Jornada - Administrador vê os pedidos com status, valor e data (administracao, jornada)
- **História:** História 3 - Administrador acompanha as vendas
- **O que a evidência mostra:** 1/3 passos; 13 erro(s) de console. passo 1 (Abre a lista de pedidos): não consegui abrir /admin/order/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/order/list
- **Leitura da revisão:** Mesma causa do login do painel (CSRF + `Host` sem porta); a lista nunca abre.
- **Evidências:** `qa-harness/evidencias/jornadas/administracao/administrador-ve-os-pedidos/monitor/01-abre-a-lista-de-pedidos.png`

### Achado 17 - Administrador procura a avaliação pendente para moderar

- **Origem:** Jornada - Administrador procura a avaliação pendente para moderar (administracao, jornada)
- **História:** História 4 - Administrador modera as avaliações
- **O que a evidência mostra:** 1/2 passos; 13 erro(s) de console. passo 1 (Abre a lista de avaliações): não consegui abrir /admin/review/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/review/list
- **Leitura da revisão:** Mesma causa do login do painel. Além disso, o código mostra que a lista de avaliações do painel não tem comentário nem status (`ReviewAdmin.column_list`) e não permite editar: moderar pela tela seria às cegas.
- **Evidências:** `qa-harness/evidencias/jornadas/administracao/administrador-ve-a-fila-de-moderacao/monitor/01-abre-a-lista-de-avaliacoes.png`

### Achado 18 - Administrador vê os cupons de desconto

- **Origem:** Jornada - Administrador vê os cupons de desconto (administracao, jornada)
- **História:** História 5 - Administrador gerencia cupons de desconto
- **O que a evidência mostra:** 1/2 passos; 13 erro(s) de console. passo 1 (Abre a lista de cupons): não consegui abrir /admin/coupon/list: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/coupon/list
- **Leitura da revisão:** Mesma causa do login do painel (CSRF + `Host` sem porta); a lista nunca abre.
- **Evidências:** `qa-harness/evidencias/jornadas/administracao/administrador-ve-os-cupons/monitor/01-abre-a-lista-de-cupons.png`

### Achado 19 - Visitante compra informando só o e-mail

- **Origem:** Jornada - Visitante compra informando só o e-mail (compra, jornada)
- **História:** História 2 - Visitante compra um e-book sem ter conta
- **O que a evidência mostra:** 6/7 passos. passo 6 (Chega à página de pagamento do pedido): a URL é http://127.0.0.1:48273/#/pedidos, esperava /pay/simulate/
- **Evidências:** `qa-harness/evidencias/jornadas/compra/visitante-compra-sem-conta/monitor/01-abre-o-e-book-python-na-pratica.png`, `qa-harness/evidencias/jornadas/compra/visitante-compra-sem-conta/monitor/02-clica-em-comprar-e-baixar-sem-e-mail.png`, `qa-harness/evidencias/jornadas/compra/visitante-compra-sem-conta/monitor/03-ve-o-pedido-de-e-mail-valido.png`, `qa-harness/evidencias/jornadas/compra/visitante-compra-sem-conta/monitor/04-digita-o-e-mail.png`, `qa-harness/evidencias/jornadas/compra/visitante-compra-sem-conta/monitor/05-clica-em-comprar-e-baixar.png`, `qa-harness/evidencias/jornadas/compra/visitante-compra-sem-conta/monitor/06-chega-a-pagina-de-pagamento-do-pedido.png`

### Achado 20 - Comprador vê os pedidos e tenta pagar o pendente

- **Origem:** Jornada - Comprador vê os pedidos e tenta pagar o pendente (compra, jornada)
- **História:** História 4 - Comprador acompanha os pedidos e retoma um pagamento pendente
- **O que a evidência mostra:** 2/6 passos. passo 2 (Clica em Pedidos): não consegui clicar: Locator.click: Timeout 20000ms exceeded.
- **Leitura da revisão:** Chega aos pedidos no healing; o pedido pendente aparece sem "Pagar" (`checkout_url` nulo em `/orders/my`) — RF-25.
- **Evidências:** `qa-harness/evidencias/jornadas/compra/comprador-retoma-pedido-pendente/monitor/01-abre-a-loja-com-a-conta.png`, `qa-harness/evidencias/jornadas/compra/comprador-retoma-pedido-pendente/monitor/02-clica-em-pedidos.png`

### Achado 21 - Visitante abre a política de privacidade e os termos pelo rodapé

- **Origem:** Jornada - Visitante abre a política de privacidade e os termos pelo rodapé (vitrine, jornada)
- **História:** História 6 - Visitante lê a política de privacidade e os termos
- **O que a evidência mostra:** 3/6 passos. passo 3 (Vê a política de privacidade): não achei "Política de Privacidade" em body
- **Evidências:** `qa-harness/evidencias/jornadas/vitrine/visitante-le-privacidade-e-termos/monitor/01-abre-a-loja.png`, `qa-harness/evidencias/jornadas/vitrine/visitante-le-privacidade-e-termos/monitor/02-clica-em-privacidade-no-rodape.png`, `qa-harness/evidencias/jornadas/vitrine/visitante-le-privacidade-e-termos/monitor/03-ve-a-politica-de-privacidade.png`

### Achado 22 - Base visual - visitante (monitor)

- **Origem:** Base visual - visitante (monitor) (base-visual, base)
- **História:** Base visual - visitante
- **O que a evidência mostra:** 7 tela(s) em monitor; 13 erro(s) de console. Todas renderizaram conteúdo, sem rolagem horizontal.
- **Leitura da revisão:** Veredito automático VALIDO pelo limiar de texto, mas `05-privacidade` e `06-termos` renderizam a home do SPA (mesmo texto de 997 caracteres de `01-home`): o nginx não repassa `/privacidade` e `/termos` ao backend. E `03-carrinho-sem-conta` e `04-pagina-inexistente` ficam com o título da aba "Python na Prática — e_seller" herdado da página anterior.
- **Evidências:** `qa-harness/evidencias/_base/visitante/monitor/01-home.png`, `qa-harness/evidencias/_base/visitante/monitor/02-detalhe-do-ebook.png`, `qa-harness/evidencias/_base/visitante/monitor/03-carrinho-sem-conta.png`, `qa-harness/evidencias/_base/visitante/monitor/04-pagina-inexistente.png`, `qa-harness/evidencias/_base/visitante/monitor/05-privacidade.png`, `qa-harness/evidencias/_base/visitante/monitor/06-termos.png`

### Achado 23 - Base visual - admin (monitor)

- **Origem:** Base visual - admin (monitor) (base-visual, base)
- **História:** Base visual - admin
- **O que a evidência mostra:** 7 tela(s) em monitor; 15 erro(s) de console. Problemas: 01-painel falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/; 02-produtos falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/product/list; 03-pedidos falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/order/list; 04-avaliacoes falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/review/list; 05-cupons falhou ao abrir: Page.goto: net::ERR_CONNECTION_REFUSED at http://127.0.0.1:48273/admin/coupon/list; 06-painel-html-de-pedidos renderizou só 28 caracteres; 07-painel-html-novo-ebook renderizou só 28 caracteres
- **Leitura da revisão:** `01` a `05` terminam em `chrome-error://` (conexão recusada): o login do SQLAdmin é barrado pelo CSRF (403) e o redirecionamento do painel vai para `http://127.0.0.1/admin/...` sem a porta — o nginx repassa `Host $host`. O console mostra os estáticos do painel vindo de `127.0.0.1` sem porta e barrados pela CSP. `06` e `07` (painéis HTML em `/api/v1/admin/*/panel`) mostram só "Não autenticado": exigem cabeçalho `Authorization`, que o navegador não envia.
- **Evidências:** `qa-harness/evidencias/_base/admin/monitor/01-painel.png`, `qa-harness/evidencias/_base/admin/monitor/02-produtos.png`, `qa-harness/evidencias/_base/admin/monitor/03-pedidos.png`, `qa-harness/evidencias/_base/admin/monitor/04-avaliacoes.png`, `qa-harness/evidencias/_base/admin/monitor/05-cupons.png`, `qa-harness/evidencias/_base/admin/monitor/06-painel-html-de-pedidos.png`

## Lacunas de especificação (lint das histórias)

Nenhuma: toda jornada cita história existente, verifica o resultado e marca INICIO e FIM.

## Revisão de validade e healing

Rodada 1 do `/qa completo` no e_seller. Auditei os 53 pontos de integração pelos `.json` (corpo e contraste), as 20 jornadas pelos prints e pelo `evidencias.json` de cada passo, e as 4 bases visuais pelas métricas de captura (URL final, título, tamanho do texto) e por imagem onde a métrica levantou dúvida. Healing de evidência feito uma vez (execução 2026-09-27-0457, modo `visual`, mesmo build do produto): o adaptador deixava a aba em `/` depois de gravar a sessão e o `abrir /#/...` seguinte só trocava o hash — o topo do SPA ficava no estado sem sessão. Corrigido o teste (adaptador sai para `about:blank`), nunca o produto. As imagens das pastas de evidência são as do healing.

- **Ponto 3 - Busca por FastAPI traz só o e-book certo**: FALHA DE PRODUTO → FALHA DE PRODUTO · healing 0 — Confirmado: `GET /api/v1/products?q=FastAPI` responde 500 no Postgres (`SELECT DISTINCT` com `ORDER BY CASE` de relevância). O SPA não cai nisso porque sempre manda `sort` (sem relevância) — por isso a jornada de busca é válida — mas o contrato `?q=` sem `sort` quebra.
- **Jornada - Comprador salva o perfil fiscal**: FALHA DE PRODUTO → FALHA DE PRODUTO · healing 1 — Na rodada parou cedo pelo defeito do adaptador; no healing percorreu os 10 passos e o toast "Perfil salvo" não aparece: a API responde 422 (`person_type` "PF" — a API espera `individual`/`company`), igual ao Ponto 6 de acesso.
- **Jornada - Administrador entra no painel pelo formulário de login**: EVIDENCIA INVALIDA → FALHA DE PRODUTO · healing 1 — Automático EVIDENCIA INVALIDA (navegação recusada), mas a causa é o produto: login do SQLAdmin barrado pelo CSRF e redirecionamento sem a porta (`Host $host` no nginx). Repetiu igual no healing.
- **Jornada - Administrador vê a lista de e-books no painel**: EVIDENCIA INVALIDA → FALHA DE PRODUTO · healing 1 — Mesma causa do login do painel (CSRF + `Host` sem porta); a lista nunca abre.
- **Jornada - Administrador vê os pedidos com status, valor e data**: EVIDENCIA INVALIDA → FALHA DE PRODUTO · healing 1 — Mesma causa do login do painel (CSRF + `Host` sem porta); a lista nunca abre.
- **Jornada - Administrador procura a avaliação pendente para moderar**: EVIDENCIA INVALIDA → FALHA DE PRODUTO · healing 1 — Mesma causa do login do painel. Além disso, o código mostra que a lista de avaliações do painel não tem comentário nem status (`ReviewAdmin.column_list`) e não permite editar: moderar pela tela seria às cegas.
- **Jornada - Administrador vê os cupons de desconto**: EVIDENCIA INVALIDA → FALHA DE PRODUTO · healing 1 — Mesma causa do login do painel (CSRF + `Host` sem porta); a lista nunca abre.
- **Jornada - Comprador vê os e-books comprados e quem não comprou vê a biblioteca vazia**: EVIDENCIA INVALIDA → VALIDO · healing 1 — Botão Biblioteca escondido pelo defeito do adaptador; no healing os 7 passos passam (cliente com os e-books, `sem_compras` com a biblioteca vazia).
- **Jornada - Comprador marca um e-book com o coração e o vê nos favoritos**: EVIDENCIA INVALIDA → VALIDO · healing 1 — Válida no healing (coração marcado, e-book em "Meus favoritos"). O console registrou um 500 em `POST /api/v1/wishlist/fastapi-do-zero`: o clique dispara dois pedidos (o SPA liga o botão duas vezes) e o segundo estoura a UNIQUE no Postgres — achado de produto registrado à parte (QAF-16).
- **Jornada - Comprador compra pelo carrinho, paga e recebe o e-book**: EVIDENCIA INVALIDA → VALIDO · healing 1 — Válida no healing (14/14: carrinho 49,90, simulador, pedido pago com "Baixar", e-book na biblioteca). Os prints do simulador e do pedido mostram HTML sem estilo (o CSS de `/static/` volta como a página do SPA), o que já é a falha do Ponto 4 de compra.
- **Jornada - Comprador vê os pedidos e tenta pagar o pendente**: EVIDENCIA INVALIDA → FALHA DE PRODUTO · healing 1 — Chega aos pedidos no healing; o pedido pendente aparece sem "Pagar" (`checkout_url` nulo em `/orders/my`) — RF-25.
- **Jornada - Visitante busca um e-book pelo título**: VALIDO → VALIDO · healing 0 — Print do passo 4 mostra só "FastAPI do Zero" com a busca preenchida; o SPA envia `sort=newest` e escapa do erro do Ponto 3.
- **Base visual - visitante (monitor)**: VALIDO → FALHA DE PRODUTO · healing 0 — Veredito automático VALIDO pelo limiar de texto, mas `05-privacidade` e `06-termos` renderizam a home do SPA (mesmo texto de 997 caracteres de `01-home`): o nginx não repassa `/privacidade` e `/termos` ao backend. E `03-carrinho-sem-conta` e `04-pagina-inexistente` ficam com o título da aba "Python na Prática — e_seller" herdado da página anterior.
- **Base visual - cliente (monitor)**: VALIDO → VALIDO · healing 1 — Na rodada o topo aparecia com "Entrar" apesar do conteúdo logado (defeito do adaptador). Depois do healing o topo mostra Carrinho, Biblioteca, Favoritos, Pedidos, Conta e o avatar com "Sair", e as telas batem com a massa (biblioteca com os e-books, pedido pago de 99,80).
- **Base visual - sem_compras (monitor)**: VALIDO → VALIDO · healing 1 — Mesmo defeito do adaptador; após o healing, biblioteca vazia e pedido pendente com a conta logada.
- **Base visual - admin (monitor)**: FALHA DE PRODUTO → FALHA DE PRODUTO · healing 0 — `01` a `05` terminam em `chrome-error://` (conexão recusada): o login do SQLAdmin é barrado pelo CSRF (403) e o redirecionamento do painel vai para `http://127.0.0.1/admin/...` sem a porta — o nginx repassa `Host $host`. O console mostra os estáticos do painel vindo de `127.0.0.1` sem porta e barrados pela CSP. `06` e `07` (painéis HTML em `/api/v1/admin/*/panel`) mostram só "Não autenticado": exigem cabeçalho `Authorization`, que o navegador não envia.

## Warnings - Convenção de comentários

Regra: .spec/code/convencao-de-comentarios.md · 16 candidato(s), 4 violação(ões). Warning não reprova a execução.

| Arquivo | Linha | Categoria | O quê | Destino |
|---|---|---|---|---|
| backend/app/orders/models.py | 40 | narrativa | docstring diz 'no MVP, 1 item' — história de fase, e o pedido já é multi-item | .spec/planning/06-escopo-mvp.md |
| frontend/public/style.css | 1 | narrativa | cabeçalho com data e épico ('Design system UXR (2026-06-13)') | .spec/frontend/roadmap-uxr.md |
| frontend/public/style.css | 119 | narrativa | 'UXR-07 — estilo; lógica na Fase 2' conta o plano de fases | .spec/frontend/roadmap-uxr.md |
| frontend/public/style.css | 128 | narrativa | 'UXR-09, base na Fase 1' conta o plano de fases | .spec/frontend/roadmap-uxr.md |

Aceitos após leitura: backend/app/accounts/router_admin.py:159 — CSS dentro de f-string (chaves dobradas), não é código comentado; backend/app/catalog/router_admin.py:230 — CSS dentro de f-string (chaves dobradas), não é código comentado; backend/app/coupons/router_admin.py:275 — CSS dentro de f-string (chaves dobradas), não é código comentado; backend/app/coupons/router_admin.py:279 — CSS dentro de f-string (chaves dobradas), não é código comentado; backend/app/orders/router.py:212 — descreve o comportamento atual do endpoint (paginação e X-Total-Count); backend/app/orders/services.py:46 — descreve o que o método faz hoje; backend/app/orders/services.py:112 — restrição presente do formato de data aceito; backend/app/orders/state_machine.py:37 — docstring no presente da transição de estado; backend/app/orders/state_machine.py:41 — docstring no presente da transição de estado; backend/app/orders/state_machine.py:45 — docstring no presente da transição de estado; backend/app/orders/state_machine.py:49 — docstring no presente da transição de estado; qa-harness/testes/api/teste_compra.py:239 — docstring no presente do que o ponto faz.

## Criados nesta execução

- `qa-harness/config.yaml` — configuração do harness (stack própria, perfis, caminhos em .spec/) (derivado de: adotar.md da skill /qa)
- `qa-harness/adaptador.py` — autenticação OAuth2, sessão no localStorage do SPA, login do SQLAdmin, massa (derivado de: adotar.md + mapa do produto)
- `qa-harness/massa_de_dados.py` — estado conhecido com prefixo qa- e contrastes (derivado de: metodologia §5)
- `qa-harness/ambiente/` — stack eseller-qa (compose, portas livres, credenciais locais) (derivado de: decisões D03, D04, D05)
- `qa-harness/testes/api/` — 5 suítes (vitrine, acesso, compra, biblioteca, administração) + base com máscara de segredos (derivado de: .spec/test/planos/*.yaml)
- `.spec/test/historias/` — 22 histórias em 5 domínios (derivado de: .spec/test/historias/_instrucao.md)
- `.spec/test/planos/` — 53 pontos de integração + catálogo da base visual (derivado de: histórias)
- `.spec/test/jornadas/` — 20 jornadas (derivado de: histórias com tela)

Criação não é aprovação: tudo acima entra na proposta de commit para aceite.

