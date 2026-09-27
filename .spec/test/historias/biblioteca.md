# Histórias de Usuário — Biblioteca, favoritos e avaliações

**Status:** vigente · **Derivado de:** `.spec/planning/05-user-stories.md` (US-06) · `.spec/planning/03-requisitos-funcionais.md` (RF-30, RF-31, RF-33) · `.spec/frontend/storefront.md` §1 (Minha Biblioteca) · `.spec/frontend/roadmap-uxr.md` (favoritos, UXR-32) · `.spec/unit/backend/wishlist/router_wishlist.md` · `.spec/unit/backend/reviews/router_reviews.md` · `.spec/unit/tests/security_testing.md` §3b · telas `#/biblioteca` (`renderLibrary`), `#/favoritos` (`renderWishlist`), avaliações em `#/produto/{slug}` (`loadReviews`) · rotas `/api/v1/library*`, `/api/v1/download/{token}`, `/api/v1/wishlist*`, `/api/v1/products/{slug}/reviews` · **Instrução:** `_instrucao.md`
**Jornadas:** `.spec/test/jornadas/biblioteca.yaml`

## História 1 - Comprador baixa um e-book da biblioteca
**Como** comprador, **quero** abrir minha biblioteca e baixar o que comprei, **para** ler o e-book.
**Fontes:** `.spec/planning/05-user-stories.md`:US-06 · RF-30, RF-31, RF-33 · `.spec/frontend/storefront.md`:§1 (`/minha-biblioteca`) · tela `#/biblioteca` · `POST /api/v1/library/{slug}/download-link` · `GET /api/v1/download/{token}`
**Critérios de aceite:**
- [ ] A biblioteca do comprador mostra os e-books comprados, cada um com "Baixar" (fonte: storefront.md §1)
- [ ] Quem não comprou nada vê "Sua biblioteca está vazia" (fonte: `renderLibrary`)
- [ ] Link válido entrega o arquivo do e-book sem expor o caminho no servidor (fonte: US-06, RF-33)
- [ ] Link expirado é negado (fonte: US-06)
- [ ] Link que atingiu o limite de downloads é negado (fonte: US-06, RF-31)
- [ ] Quem não possui o e-book não consegue gerar link de download (fonte: `.spec/unit/tests/security_testing.md` §3b)

## História 2 - Comprador guarda e-books nos favoritos
**Como** comprador, **quero** marcar e-books com o coração, **para** comprar depois.
**Fontes:** `.spec/frontend/roadmap-uxr.md` (UXR-32, página de favoritos) · `.spec/unit/backend/wishlist/router_wishlist.md` · tela `#/favoritos` (`renderWishlist`, `.btn-wish`) · `POST /api/v1/wishlist/{slug}`
**Critérios de aceite:**
- [ ] O coração no cartão adiciona o e-book e ele aparece em "Meus favoritos" (fonte: UXR-32, router_wishlist.md)

## História 3 - Comprador avalia um e-book que comprou
**Como** comprador, **quero** dar nota e comentar um e-book que comprei, **para** ajudar outros leitores.
**Fontes:** `.spec/unit/backend/reviews/router_reviews.md` · `.spec/unit/tests/security_testing.md` §3b ("review de comprador verificado") · tela `#/produto/{slug}` (`#rev-rating`, `#rev-comment`, `#rev-send`) · `POST /api/v1/products/{slug}/reviews`
**Critérios de aceite:**
- [ ] Quem comprou envia nota e comentário e vê "Avaliação enviada!" (fonte: router_reviews.md)
- [ ] Quem não comprou é recusado com "Só quem comprou pode avaliar" (fonte: security_testing.md §3b)
- [ ] A avaliação só aparece na página do e-book depois de aprovada pela moderação (fonte: router_reviews.md)
