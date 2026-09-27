# Roadmap VIS — Tapa visual do storefront (Material Design 3, vanilla)

> Épico **VIS**. Pedido do dono (2026-09-27): "parece um blog de ensino médio" — falta
> "magia". Modernizar com **Material Design 3** sem trocar a paleta nem a stack
> (HTML + CSS + JS puro, sem build, sem framework). **Responsividade é obrigatória.**
> Base: [`roadmap-uxr.md`](roadmap-uxr.md) (tokens e componentes do UXR continuam valendo)
> e [`../quality-bar.md`](../quality-bar.md) §3.

---

## Princípios

1. **Paleta preservada.** Roxo `#6d5cff` é a cor primária (marca); laranja `#ff7a3c` é o
   CTA de compra; fundo claro. O que muda é **como** a cor é usada: papéis de cor do M3
   (primary, primary-container, surface-container em camadas, outline-variant).
2. **Material 3 como linguagem**, não como biblioteca: formas generosas (cards 20–28px,
   botões em pílula), elevação tonal, *state layers* (hover 8%, pressionado 12%), foco
   visível, movimento com a curva *emphasized* `cubic-bezier(.2,0,0,1)`.
3. **Magia com parcimônia:** capa gerada com cara de livro (título e autor na capa,
   lombada, textura), *ripple* nos botões, app bar com vidro fosco que ganha elevação
   ao rolar, entrada suave das telas, cards que sobem no hover. Nada que atrase a
   primeira pintura: sem fontes nem scripts externos.
4. **Contrato de seletores estável:** ids e classes que o JS e o `/qa` usam
   (`#auth-btn`, `#lib-btn`, `#cart-btn`, `#orders-btn`, `#wish-btn`, `#search-input`,
   `#product-grid`, `a.card`, `.btn-wish`, `#buy-btn`, `#cart-checkout`...) não mudam.
5. **Mobile-first e acessível:** alvo de toque ≥ 40px, contraste AA no texto,
   `prefers-reduced-motion` desliga animações, sem rolagem horizontal em 390px.

---

## Itens

| ID | Tela / componente | Entrega |
|---|---|---|
| VIS-01 | Tokens | Papéis de cor M3 derivados da paleta, escala tipográfica (display/headline/title/body/label), formas, elevação, movimento |
| VIS-02 | Top app bar | Vidro fosco + elevação ao rolar; busca em pílula com botão de buscar visível (`#search-btn`); ações como *icon buttons* tonais |
| VIS-03 | Hero | Headline display com destaque em gradiente da marca, brilho animado de fundo (pausável), CTA em pílula, prova social em chip |
| VIS-04 | Capa gerada | Capa de livro: gradiente pela cor derivada do título, lombada, textura, título + autor tipografados na capa |
| VIS-05 | Cards | Card elevado M3 (raio 20px), mídia 2:3, hover com elevação e zoom da capa, preço em destaque, CTA tonal |
| VIS-06 | Chips e filtros | *Filter chips* M3 (selecionado = container tonal com ✓), ordenação como *select* outlined |
| VIS-07 | Detalhe | Layout em duas colunas com capa grande e sombra de livro; *buy box* em surface-container com botões pílula; avaliações em cards |
| VIS-08 | Diálogo de login | Diálogo M3 (raio 28px, scrim, entrada com escala), abas com indicador |
| VIS-09 | Snackbars | Toasts como *snackbars* M3 no rodapé central |
| VIS-10 | Estados | Vazio, erro e 404 com ícone em círculo tonal; skeleton com brilho |
| VIS-11 | Carrinho, biblioteca, pedidos, conta, favoritos | Mesma linguagem (cards, listas, campos outlined) |
| VIS-12 | Movimento | *Ripple* (JS), entrada das telas, `prefers-reduced-motion` |
| VIS-13 | Responsivo | Celular (390px): app bar em duas linhas, menu em folha, grade 2 colunas; notebook (1366px) e monitor |
| VIS-14 | Páginas do backend (simulador, pedido, institucionais, recuperar senha) | Passam ao **tema claro da loja**: os tokens de `backend/app/web/static/css/design-system.css` viram os papéis M3 claros da marca (o tema escuro do FEV some) — no meio da compra a página não pode parecer outro site. CSS servido pelo nginx (QAF-09) |

---

## Critérios de aceite do épico

- [ ] Paleta de marca preservada (roxo primário, laranja de compra)
- [ ] Nenhum seletor usado pelo JS ou pelas jornadas do `/qa` removido ou renomeado
- [ ] `/qa completo` sem regressão funcional nas jornadas do storefront
- [ ] `/qa responsividade` sem rolagem horizontal e sem elemento inacessível em celular e notebook
- [ ] Sem dependência externa nova (fonte, CDN, framework)
- [ ] `prefers-reduced-motion` respeitado
