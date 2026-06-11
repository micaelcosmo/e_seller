# 05 — User Stories e Critérios de Aceite

> Documento de planning · e_seller · 2026-06-06
> Histórias no formato "Como… quero… para…", com critérios de aceite em **Gherkin**
> (Dado/Quando/Então). Estes critérios são a **base dos testes (TDD)**.

---

## 💡 Por que Gherkin?

O formato **Dado / Quando / Então** descreve comportamento observável sem falar de
implementação. Cada cenário vira, quase 1-para-1, um caso de teste. Isso conecta
SDD (a spec) com TDD (o teste que escrevemos antes do código).

---

## US-01 — Navegar catálogo (RF-01)
**Como** leitor, **quero** ver os e-books disponíveis **para** escolher o que comprar.

```gherkin
Cenário: Listar e-books publicados
  Dado que existem 3 e-books publicados e 1 em rascunho
  Quando eu acesso a página de catálogo
  Então vejo 3 e-books
  E não vejo o e-book em rascunho
```

## US-02 — Ver detalhe do e-book (RF-02)
**Como** leitor, **quero** ver os detalhes de um e-book **para** decidir a compra.

```gherkin
Cenário: Abrir detalhe
  Dado um e-book publicado "Python na Prática" por R$ 39,90
  Quando eu acesso a página de detalhe dele
  Então vejo título, autor, descrição e o preço R$ 39,90
```

## US-03 — Cadastrar e-book (RF-10, RF-12)
**Como** administrador, **quero** cadastrar um e-book **para** colocá-lo à venda.

```gherkin
Cenário: Criar produto válido
  Dado que estou autenticado no Admin
  Quando crio um e-book com título, preço e arquivo PDF válido
  Então o e-book é salvo como rascunho

Cenário: Rejeitar arquivo inválido
  Dado que estou autenticado no Admin
  Quando tento subir um arquivo .exe como e-book
  Então recebo erro de validação de tipo de arquivo
```

## US-04 — Iniciar compra (RF-20, RF-21, RF-22)
**Como** leitor, **quero** iniciar a compra **para** pagar pelo e-book.

```gherkin
Cenário: Criar pedido pendente e checkout
  Dado um e-book publicado por R$ 39,90
  Quando informo meu e-mail e confirmo a compra
  Então um pedido é criado com status "pendente"
  E sou direcionado ao checkout do Mercado Pago
```

## US-05 — Confirmar pagamento via webhook (RF-23, RF-24, RNF-01, RNF-20)
**Como** sistema, **quero** processar o webhook **para** liberar a entrega só quando pago.

```gherkin
Cenário: Pagamento aprovado
  Dado um pedido "pendente"
  Quando recebo um webhook válido informando pagamento aprovado
  Então o pedido passa para "pago"
  E um link de download é gerado

Cenário: Webhook duplicado (idempotência)
  Dado um pedido já "pago" por um webhook anterior
  Quando recebo novamente o mesmo webhook
  Então o pedido continua "pago"
  E nenhum novo link/efeito duplicado é criado

Cenário: Retorno do navegador sem webhook
  Dado um pedido "pendente"
  Quando o navegador retorna à página de sucesso sem webhook confirmado
  Então o download NÃO é liberado
```

## US-06 — Baixar e-book (RF-30, RF-31, RF-33, RNF-03)
**Como** leitor que pagou, **quero** baixar o e-book **para** lê-lo.

```gherkin
Cenário: Download válido
  Dado um pedido "pago" com link de download válido
  Quando acesso o link
  Então recebo o arquivo do e-book

Cenário: Link expirado
  Dado um link de download expirado
  Quando acesso o link
  Então recebo erro de link inválido/expirado

Cenário: Limite de downloads atingido
  Dado um pedido cujo limite de downloads foi atingido
  Quando tento baixar novamente
  Então o download é negado
```

## US-07 — Acompanhar vendas (RF-40)
**Como** administrador, **quero** ver os pedidos **para** acompanhar as vendas.

```gherkin
Cenário: Listar pedidos
  Dado que existem pedidos em vários status
  Quando acesso a lista de pedidos no Admin
  Então vejo cada pedido com status, valor e data
```

---

## Rastreabilidade

Cada cenário acima deve ter um teste correspondente (ver
[`13-estrategia-de-testes.md`](13-estrategia-de-testes.md)). Nenhum código de
produção é escrito sem que o cenário-teste exista e falhe primeiro.
