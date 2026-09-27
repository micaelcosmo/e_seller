# Histórias de Usuário — Administração

**Status:** vigente · **Derivado de:** `.spec/planning/05-user-stories.md` (US-03, US-07) · `.spec/planning/03-requisitos-funcionais.md` (RF-10..RF-12, RF-40..RF-42, RF-50) · `.spec/unit/backend/admin/*.md` · `.spec/unit/backend/reviews/router_reviews.md` · `.spec/unit/backend/coupons/router_coupons.md` · `.spec/unit/tests/security_testing.md` (RBAC) · telas `/admin` (SQLAdmin, `backend/app/admin/`) · rotas `/api/v1/admin/*`, `/api/v1/orders` · **Instrução:** `_instrucao.md`
**Jornadas:** `.spec/test/jornadas/administracao.yaml`

## História 1 - Administrador entra no painel administrativo
**Como** administrador, **quero** entrar no painel com meu e-mail e senha, **para** gerenciar a loja.
**Fontes:** RF-50 · `.spec/unit/backend/admin/admin_auth_backend.md` · `.spec/unit/backend/admin/sqladmin_setup.md` · tela `/admin/login` · `.spec/unit/tests/security_testing.md` (RBAC)
**Critérios de aceite:**
- [ ] Com e-mail e senha de administrador o painel `/admin` abre com os cadastros (Produtos, Pedidos) (fonte: admin_auth_backend.md, sqladmin_setup.md)
- [ ] Comprador não acessa a API de administração (403) (fonte: security_testing.md, RBAC)
- [ ] Sem login a API de administração recusa (401) (fonte: security_testing.md, RBAC)

## História 2 - Administrador cadastra e publica um e-book
**Como** administrador, **quero** cadastrar um e-book e publicá-lo, **para** colocá-lo à venda.
**Fontes:** `.spec/planning/05-user-stories.md`:US-03 · RF-10, RF-11, RF-12 · `.spec/unit/backend/admin/admin_views_product.md` · `POST /api/v1/admin/products`, `PATCH /api/v1/admin/products/{slug}/status`, `POST /api/v1/admin/products/{slug}/upload-file` · tela `/admin/product/list`
**Critérios de aceite:**
- [ ] Criar e-book com título e preço salva como rascunho, fora da vitrine (fonte: US-03, RF-11)
- [ ] Arquivo `.exe` é recusado como e-book (fonte: US-03, RF-12)
- [ ] Publicar o e-book faz ele aparecer na vitrine (fonte: RF-11)
- [ ] O e-book cadastrado aparece na lista de produtos do painel (fonte: admin_views_product.md)
- [ ] O e-book cadastrado com arquivo é entregue a quem o compra (download do arquivo enviado) (fonte: US-03 + US-06, RF-12, RF-30)

## História 3 - Administrador acompanha as vendas
**Como** administrador, **quero** ver os pedidos com status, valor e data, **para** acompanhar as vendas.
**Fontes:** `.spec/planning/05-user-stories.md`:US-07 · RF-40, RF-41, RF-42 · `.spec/unit/backend/admin/admin_views_order.md` · `GET /api/v1/orders`, `GET /api/v1/orders/admin/{reference}`, `GET /api/v1/admin/reports/sales` · tela `/admin/order/list`
**Critérios de aceite:**
- [ ] A lista de pedidos mostra cada pedido com status, valor e data (fonte: US-07, RF-40)
- [ ] O detalhe de um pedido mostra itens e status (fonte: RF-41)
- [ ] O relatório de vendas por período soma os pedidos pagos (fonte: RF-42)

## História 4 - Administrador modera as avaliações
**Como** administrador, **quero** aprovar ou recusar avaliações pendentes, **para** só publicar o que é adequado.
**Fontes:** `.spec/unit/backend/reviews/router_reviews.md` · `GET /api/v1/admin/reviews`, `PATCH /api/v1/admin/reviews/{id}/moderate` · telas `/admin/review/list` e `#/produto/{slug}` (avaliações publicadas)
**Critérios de aceite:**
- [ ] A avaliação pendente aparece na fila de moderação (fonte: router_reviews.md)
- [ ] Aprovar a avaliação faz ela aparecer na página do e-book (fonte: router_reviews.md)

## História 5 - Administrador gerencia cupons de desconto
**Como** administrador, **quero** criar e desativar cupons, **para** controlar promoções.
**Fontes:** RF-26 · `.spec/unit/backend/coupons/router_coupons.md` · `POST /api/v1/admin/coupons`, `PATCH /api/v1/admin/coupons/{code}/toggle`, `POST /api/v1/coupons/validate` · tela `/admin/coupon/list`
**Critérios de aceite:**
- [ ] Os cupons existentes aparecem na lista de cupons do painel (fonte: router_coupons.md)
- [ ] Criar um cupom faz ele valer na validação de cupom (fonte: router_coupons.md)
- [ ] Desativar o cupom faz a validação recusá-lo (fonte: router_coupons.md)
