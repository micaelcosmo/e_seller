# 03 — Requisitos Funcionais (RF)

> Documento de planning · e_seller · 2026-06-06
> O que o sistema **deve fazer**. Cada RF é rastreável até user stories e testes.

---

## Convenção

- `RF-XX` — identificador estável.
- Prioridade: **Must** (MVP), **Should** (importante), **Could** (desejável), **Won't** (fora por ora) — método MoSCoW.

---

## Catálogo

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | Listar e-books publicados com capa, título, autor e preço. | Must |
| RF-02 | Exibir página de detalhe de um e-book (descrição, prévia, preço). | Must |
| RF-03 | Buscar e-books por título/autor. | Should |
| RF-04 | Filtrar/ordenar por categoria e preço. | Could |

## Produtos (administração) — P2

| ID | Requisito | Prioridade |
|---|---|---|
| RF-10 | Criar/editar/remover e-book (metadados, capa, arquivo, preço). | Must |
| RF-11 | Definir status do produto: rascunho / publicado. | Must |
| RF-12 | Upload do arquivo do e-book (PDF/EPUB) com validação de tipo e tamanho. | Must |
| RF-13 | Organizar produtos por categoria. | Should |

## Compra & Pagamento — P1

| ID | Requisito | Prioridade |
|---|---|---|
| RF-20 | Iniciar compra de um e-book informando e-mail do comprador. | Must |
| RF-21 | Criar pedido (Order) no estado "pendente". | Must |
| RF-22 | Gerar preferência/checkout no Mercado Pago. | Must |
| RF-23 | Receber webhook do Mercado Pago e atualizar o pedido de forma idempotente. | Must |
| RF-24 | Marcar pedido como "pago" somente após confirmação válida do webhook. | Must |
| RF-25 | Permitir reiniciar pagamento de um pedido pendente. | Should |
| RF-26 | Suportar cupons de desconto. | Could / Won't (MVP) |

## Entrega digital — P1

| ID | Requisito | Prioridade |
|---|---|---|
| RF-30 | Gerar link de download seguro, único e expirável após pagamento aprovado. | Must |
| RF-31 | Limitar número de downloads por pedido. | Must |
| RF-32 | Enviar e-mail ao comprador com o acesso ao download. | Should |
| RF-33 | Servir o arquivo sem expor o caminho real de armazenamento. | Must |

## Pedidos & relatórios — P2

| ID | Requisito | Prioridade |
|---|---|---|
| RF-40 | Listar pedidos com status, valor e data (no Admin). | Must |
| RF-41 | Visualizar detalhe de um pedido e seu histórico de status. | Should |
| RF-42 | Exportar/relatar vendas por período. | Could |

## Contas & acesso

| ID | Requisito | Prioridade |
|---|---|---|
| RF-50 | Autenticar administradores (OAuth2 + JWT; ver ADR-007). | Must |
| RF-51 | Compra como convidado (sem cadastro), identificada por e-mail. | Must |
| RF-52 | Conta de leitor com histórico de compras. | Could |

---

## Rastreabilidade

Cada RF "Must" terá ao menos uma **user story** com critérios de aceite em
[`05-user-stories.md`](05-user-stories.md) e, por TDD, ao menos um **teste** que
falhe antes da implementação.
