# Histórias de Usuário — Compra e pagamento

**Status:** vigente · **Derivado de:** `.spec/planning/05-user-stories.md` (US-04, US-05) · `.spec/planning/03-requisitos-funcionais.md` (RF-20..RF-26, RF-51, RF-52) · `.spec/frontend/storefront.md` §2 (fluxo de compra) · `.spec/unit/backend/coupons/router_coupons.md` · telas `#/produto/{slug}` (`buy`), `#/carrinho` (`renderCart`), `#/pedidos` (`renderOrders`), `/pay/simulate/{reference}` e `/pedido/{reference}` · rotas `/api/v1/orders*`, `/api/v1/cart/*`, `/api/v1/coupons/validate`, `/pay/confirm/{reference}`, `/api/v1/webhooks/mercadopago` · **Instrução:** `_instrucao.md`
**Jornadas:** `.spec/test/jornadas/compra.yaml`

## História 1 - Comprador compra pelo carrinho e paga
**Como** comprador, **quero** pôr um e-book no carrinho, finalizar e pagar, **para** receber o e-book na hora.
**Fontes:** `.spec/planning/05-user-stories.md`:US-04, US-05 · `.spec/frontend/storefront.md`:§2 · tela `#/carrinho` (`renderCart`, `cartCheckout`) · `/pay/simulate/{reference}` · `/pedido/{reference}`
**Critérios de aceite:**
- [ ] Adicionar "FastAPI do Zero" ao carrinho mostra o item e o total R$ 49,90 (fonte: storefront.md §6; `renderCart`)
- [ ] "Finalizar compra" leva à página de pagamento do pedido (fonte: US-04)
- [ ] Aprovar o pagamento mostra o pedido como pago, com o download disponível (fonte: US-05, US-06) [limitação de ambiente] (Mercado Pago real desligado; pagamento pelo simulador `fake`)
- [ ] As páginas de pagamento e de pedido aparecem com o visual da loja, não como HTML cru (fonte: `.spec/quality-bar.md` §3)
- [ ] Depois de pago, o e-book aparece na biblioteca do comprador (fonte: RF-52; storefront.md §2)

## História 2 - Visitante compra um e-book sem ter conta
**Como** visitante, **quero** comprar informando só o meu e-mail, **para** não precisar criar conta.
**Fontes:** `.spec/planning/05-user-stories.md`:US-04 · RF-20, RF-21, RF-22, RF-51 · `.spec/frontend/storefront.md`:§1 ("compra como convidado") e §2 · tela `#/produto/{slug}` (`#buy-email`, `#buy-btn`) · `POST /api/v1/orders`
**Critérios de aceite:**
- [ ] Informar o e-mail e clicar "Comprar e baixar" cria o pedido pendente e leva ao pagamento (fonte: US-04, RF-20, RF-21, RF-22)
- [ ] Sem um e-mail válido a compra não segue e a tela pede "Informe um e-mail válido." (fonte: `buy` em `frontend/public/app.js`)

## História 3 - Comprador usa um cupom de desconto
**Como** comprador, **quero** aplicar um cupom, **para** pagar menos.
**Fontes:** RF-26 · `.spec/unit/backend/coupons/router_coupons.md` · `backend/seeds/dev_coupons.json` (`BEMVINDO10`, 10%) · tela `#/produto/{slug}` (`#buy-coupon`, `bindCouponValidation`) · `POST /api/v1/coupons/validate`
**Critérios de aceite:**
- [ ] O cupom BEMVINDO10 em "Python na Prática" mostra "Cupom válido" com o total R$ 35,91 (fonte: RF-26, dev_coupons.json)
- [ ] Cupom inexistente mostra "Cupom inválido ou expirado" (fonte: `bindCouponValidation`)
- [ ] O pedido criado com o cupom é gravado com o valor já com desconto (fonte: RF-26)

## História 4 - Comprador acompanha os pedidos e retoma um pagamento pendente
**Como** comprador, **quero** ver meus pedidos e pagar um que ficou pendente, **para** não perder a compra.
**Fontes:** RF-25, RF-52 · tela `#/pedidos` (`renderOrders`) · `GET /api/v1/orders/my`
**Critérios de aceite:**
- [ ] "Meus pedidos" lista cada pedido com o status e o valor (fonte: RF-52)
- [ ] Pedido pendente oferece um jeito de pagar ("Pagar") (fonte: RF-25)

## História 5 - Sistema confirma o pagamento pelo webhook
**Como** sistema de pagamento, **quero** avisar a loja que o pagamento foi aprovado, **para** a entrega ser liberada só quando pago.
**Prova visual:** não se aplica — o ator é o provedor de pagamento chamando o webhook; não há tela.
**Fontes:** `.spec/planning/05-user-stories.md`:US-05 · RF-23, RF-24 · `POST /api/v1/webhooks/mercadopago`
**Critérios de aceite:**
- [ ] Webhook de pagamento aprovado muda o pedido para pago e libera o download (fonte: US-05)
- [ ] O mesmo webhook repetido não repete efeito (fonte: US-05, idempotência)
- [ ] Pedido ainda pendente não libera download (fonte: US-05, "retorno do navegador sem webhook")
