# Pesquisa de Mercado — Plataformas de Venda de E-books

> Coleta: 2026-06-13. Metodologia: WebFetch em 10 de 12 sites (Kobo e bundles.io
> bloquearam acesso automatizado). Hex inferidos quando não explícitos no markup.

---

## Padrões de consenso de mercado (8+/10 sites)

| Padrão | Frequência |
|---|---|
| Background branco como base | 10/10 |
| CTA primário em azul ou verde saturado (nunca vermelho) | 8/10 |
| Sans-serif como família tipográfica | 10/10 |
| Header: logo esquerdo + CTA direito | 9/10 |
| Footer multi-coluna com links legais | 10/10 |
| Ícones de redes sociais no footer | 10/10 |
| Prova social (depoimentos / métricas) | 9/10 |
| Whitespace generoso entre seções | 9/10 |
| Cards sem borda visível (flat ou sombra sutil) | 8/10 |

### Paleta — consenso
- **Background:** branco puro / off-white universal
- **Texto:** cinza escuro (#222–#333) ou preto
- **CTA primário:** azul (maioria) ou verde (Gumroad); nunca vermelho
- **Accent secundário:** amarelo/laranja para destaques (Eduzz, Hotmart)
- **Gradiente:** só Hotmart usa no hero; resto prefere flat

### Tipografia — consenso
- Sans-serif exclusivamente; nenhum site usa serif no corpo
- Body ≈ 16px
- Hero headline 36–64px, peso bold/extra-bold

### Cards — consenso
- **Border-radius:** 4–12px (suave)
- **Sombra:** box-shadow muito sutil (elevation 1–2dp) ou ausente
- **Conteúdo:** capa + título + preço + CTA (nesta ordem)
- **Hover:** elevação de sombra ou leve opacidade

### Grid — consenso
- Desktop: 3–4 colunas (marketplaces puros como Kobo usam 5–6)
- Mobile-first em todos os sites pós-2020
- Gap 16–24px entre cards

---

## Destaques por site (referências para o e_seller)

### Gumroad
- Estética editorial/zine, ilustrações SVG de moedas
- Métrica ao vivo: "$2,102,317 paid out this week"
- CTA verde-teal. Depoimentos com foto real.

### Leanpub
- Carrossel horizontal de capas ("shelf display") — experiência de livraria
- CTA teal (#17A2B8). Cards com box-shadow sutil, radius 4–8px.

### Sellfy
- **Mascote "Alfie"** — personagem ilustrado recorrente (brand)
- Tabela comparativa vs. concorrentes. Ícones SVG consistentes.

### Payhip
- Carrinho no topo-direito com **contador de itens + total em tempo real**
- "Trusted by 130,000+ creators". Cards minimalistas alto contraste.

### Podia
- Posicionamento "human-centered", tom editorial caloroso
- next/image otimizado, feature cards alternados.

### Hotmart
- **Gradiente laranja-marrom quente no hero** — identidade forte
- Rating "4.9" com 350k+ avaliações. Stars amarelas.

### Kiwify (BR)
- FAQ em accordion. Testimonials de sucesso. CNPJ no footer.

### Eduzz (BR)
- Accent azul (#0066CC) + amarelo secundário
- Banners PIX/Boleto. Posicionamento "ecossistema".

### Smashwords
- Interface utilitária datada (anti-referência de UX).

---

## Recomendação estratégica para o e_seller

O consenso é claro: **fundo branco, CTA azul/verde saturado, sans-serif 16px,
grid 3–4 colunas, cards flat com sombra mínima (radius 8px), hero com headline
de impacto + prova social**.

**Para diferenciar**, escolher 1–2 elementos fora do consenso:
1. **Accent quente** complementar ao roxo atual (como Hotmart) — gradiente sutil no hero
2. **Prova social ao vivo** (como Gumroad/Payhip) — "X e-books vendidos", contador no carrinho
3. **Carrossel de capas** (como Leanpub) — seção "Destaques" / "Mais vendidos"

**Decisão para o e_seller:** manter o accent roxo `#6d5cff` (já é identidade),
adicionar accent quente secundário para CTAs de compra, gradiente sutil no hero,
contador no carrinho, seção de destaques em carrossel, prova social no hero.
