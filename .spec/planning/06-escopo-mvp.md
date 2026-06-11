# 06 — Escopo do MVP

> Documento de planning · e_seller · 2026-06-06
> O **menor produto** que entrega valor real: vender e entregar um e-book com segurança.

---

## 1. Princípio

O MVP existe para validar o **fluxo de ponta a ponta**: catálogo → compra →
pagamento confirmado → entrega segura. Tudo que não serve a esse fluxo fica fora.

## 2. Dentro do MVP (Must)

- **Backend API (FastAPI)** servindo JSON; **backend e frontend separados**.
- **Catálogo** via API: listagem (RF-01) e detalhe (RF-02).
- **Administração** via painel **SQLAdmin**: CRUD de e-book (RF-10), status rascunho/publicado
  (RF-11), upload validado (RF-12).
- **Compra como convidado** por e-mail (RF-51, RF-20, RF-21).
- **Pagamento Mercado Pago**: checkout (RF-22) + webhook idempotente (RF-23, RF-24).
- **Entrega segura**: link único/expirável (RF-30), limite de downloads (RF-31),
  arquivo protegido (RF-33).
- **Pedidos no painel admin** (RF-40).
- **Autenticação de admin** (RF-50).
- **Infra Docker** (backend/db; front quando definido) e PEP 8/TDD desde o início.

## 3. Fora do MVP (Should/Could/Won't por ora)

- Busca/filtre avançados (RF-03, RF-04) → próxima fase.
- Conta de leitor com histórico (RF-52).
- Cupons de desconto (RF-26).
- E-mail transacional ao comprador (RF-32) → desejável, mas o download na tela já cobre o mínimo.
- Relatórios exportáveis (RF-42).
- Marketplace multi-vendedor, reader online, nota fiscal.

## 4. Critérios de aceite do MVP (Definition of MVP-Done)

O MVP está pronto quando, com tudo rodando via `docker compose`:

1. Um admin publica um e-book pelo Admin.
2. Um visitante navega o catálogo e abre o detalhe.
3. O visitante compra informando e-mail e é levado ao checkout do Mercado Pago.
4. Após pagamento aprovado (webhook), o pedido vira "pago".
5. O visitante baixa o arquivo por um link seguro; um segundo webhook idêntico não
   duplica nada; o download respeita expiração e limite.
6. Todos os cenários "Must" de [`05-user-stories.md`](05-user-stories.md) têm testes verdes.

## 5. Sequência sugerida (entra em detalhe no roadmap)

1. Esqueleto Docker + FastAPI + healthcheck.
2. Modelo de domínio (Produto, Pedido) com SQLAlchemy + Alembic + painel admin (SQLAdmin).
3. Catálogo via API.
4. Pedido + checkout Mercado Pago (sandbox).
5. Webhook idempotente + máquina de estados do pedido.
6. Entrega segura (link expirável + limite).

> Detalhamento e marcos em [`21-roadmap.md`](21-roadmap.md).

## 6. Decisões pendentes que afetam o escopo

- [ ] Multi-vendedor? (assumindo **não** no MVP — operação única).
- [ ] E-mail transacional no MVP? (assumindo **não**, download na tela).
- [ ] Categorias já no MVP? (assumindo **simples/opcional**).
