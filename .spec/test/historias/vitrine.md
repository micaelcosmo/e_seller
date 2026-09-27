# Histórias de Usuário — Vitrine

**Status:** vigente · **Derivado de:** `.spec/planning/05-user-stories.md` (US-01, US-02) · `.spec/planning/03-requisitos-funcionais.md` (RF-01..RF-04) · `.spec/planning/19-seguranca-e-lgpd.md` · `.spec/frontend/storefront.md` §1 · `.spec/frontend/roadmap-uxr.md` · `.spec/unit/backend/newsletter/router_newsletter.md` · telas `frontend/public/app.js` (`renderHome`, `renderProduct`) e `frontend/public/index.html` (rodapé) · rotas `/api/v1/products*`, `/api/v1/newsletter/subscribe` · **Instrução:** `_instrucao.md`
**Jornadas:** `.spec/test/jornadas/vitrine.yaml`

## História 1 - Visitante conhece a loja e o catálogo
**Como** visitante, **quero** abrir a loja e ver os e-books publicados, **para** escolher o que comprar.
**Fontes:** `.spec/planning/05-user-stories.md`:US-01 · `.spec/planning/03-requisitos-funcionais.md`:RF-01 · `.spec/frontend/roadmap-uxr.md`:Fase 4 · tela `#/` (`renderHome`) · `GET /api/v1/products`
**Critérios de aceite:**
- [ ] A página inicial mostra a proposta da loja, o botão "Ver catálogo" e a prova social com o número de e-books (fonte: `.spec/frontend/roadmap-uxr.md` Fase 4)
- [ ] O catálogo lista os 3 e-books publicados com título, autor e preço (fonte: US-01, RF-01)
- [ ] O e-book em rascunho não aparece no catálogo nem abre pelo endereço direto (fonte: US-01)

## História 2 - Visitante busca um e-book por título ou autor
**Como** visitante, **quero** buscar pelo título ou autor, **para** achar rápido o e-book que procuro.
**Fontes:** `.spec/planning/03-requisitos-funcionais.md`:RF-03 · tela `#/` (`#search-input`) · `GET /api/v1/products?q=`
**Critérios de aceite:**
- [ ] Buscar "FastAPI" mostra "FastAPI do Zero" e não mostra "Python na Prática" (fonte: RF-03)

## História 3 - Visitante filtra e ordena o catálogo por preço
**Como** visitante, **quero** filtrar por faixa de preço e ordenar, **para** achar um e-book que caiba no meu bolso.
**Fontes:** `.spec/planning/03-requisitos-funcionais.md`:RF-04 · `.spec/frontend/roadmap-uxr.md`:Fase 3 (filtro por preço) · tela `#/` (chips de preço, `#sort-select`) · `GET /api/v1/products?price_min=&sort=`
**Critérios de aceite:**
- [ ] Filtrar por "R$ 50+" mostra só "Arquitetura Limpa na Web" (fonte: RF-04, roadmap-uxr Fase 3)
- [ ] Ordenar por menor preço põe "Python na Prática" (R$ 39,90) antes dos demais (fonte: RF-04)

## História 4 - Visitante vê o detalhe de um e-book
**Como** visitante, **quero** abrir a página de um e-book, **para** decidir a compra.
**Fontes:** `.spec/planning/05-user-stories.md`:US-02 · RF-02 · `.spec/frontend/roadmap-uxr.md`:Fase 5 (breadcrumb, selos) · tela `#/produto/{slug}` (`renderProduct`) · `GET /api/v1/products/{slug}`
**Critérios de aceite:**
- [ ] O detalhe mostra título, autor, descrição e o preço R$ 39,90 (fonte: US-02)
- [ ] O detalhe mostra o caminho "Início › título" e a caixa "Comprar agora" com os selos de confiança (fonte: roadmap-uxr Fase 5)
- [ ] Endereço de e-book inexistente mostra "Produto não encontrado" (fonte: `renderProduct` em `frontend/public/app.js`)

## História 5 - Visitante assina a newsletter
**Como** visitante, **quero** deixar meu e-mail no rodapé, **para** receber novidades da loja.
**Fontes:** `.spec/unit/backend/newsletter/router_newsletter.md` · tela rodapé (`#news-form`) · `POST /api/v1/newsletter/subscribe`
**Critérios de aceite:**
- [ ] Assinar com um e-mail válido confirma a inscrição na tela (fonte: router_newsletter.md)
- [ ] Assinar de novo com o mesmo e-mail não duplica nem dá erro (fonte: router_newsletter.md)

## História 6 - Visitante lê a política de privacidade e os termos
**Como** visitante, **quero** abrir a política de privacidade e os termos de uso pelo rodapé, **para** saber como meus dados são tratados antes de comprar.
**Fontes:** `.spec/planning/19-seguranca-e-lgpd.md` ("política de privacidade clara no portal") · `frontend/public/index.html` (links "Privacidade" e "Termos de uso") · `backend/app/web/router.py` (`/privacidade`, `/termos`)
**Critérios de aceite:**
- [ ] O link "Privacidade" do rodapé abre a política de privacidade (fonte: 19-seguranca-e-lgpd.md)
- [ ] O link "Termos de uso" do rodapé abre os termos de uso (fonte: 19-seguranca-e-lgpd.md)
