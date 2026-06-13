# Roadmap UXR — UX Redesign do Storefront

> Épico **UXR**. Baseado em [`ux-audit.md`](ux-audit.md) (estado atual) e
> [`market-research.md`](market-research.md) (consenso de 10 plataformas).
> Início: 2026-06-13. Meta inicial: 25 tasks, expansível até 250.

---

## Princípios

1. **Não jogar fora o que funciona** — a paleta de tokens CSS e o skeleton loader ficam.
2. **Manter identidade** — accent roxo `#6d5cff` é a marca; adicionar (não substituir).
3. **Consenso de mercado como base, diferenciação consciente** — fundo claro,
   sans-serif 16px, grid 3–4 col, cards flat radius 8px + 1–2 elementos próprios.
4. **Mobile-first** — todo componente novo nasce responsivo.
5. **Zero hardcode de dados** — textos de marketing/prova social via config quando dinâmicos.

---

## De-Para (estado atual → alvo)

| Dimensão | Hoje | Alvo (referência de mercado) |
|---|---|---|
| **Paleta** | 1 accent roxo, tudo flat sem profundidade | + accent quente para CTA-compra; tons intermediários de superfície; gradiente sutil no hero (ref. Hotmart) |
| **Tipografia** | system-ui em tudo | fonte de display no hero/headings (sans bold), body 16px mantido |
| **Hero** | só H1+sub, sem ação | + CTA "Ver catálogo" + prova social ("X e-books, download na hora") (ref. Gumroad/Payhip) |
| **Header** | botões texto, sem badge carrinho | badge numérico no carrinho com total (ref. Payhip); ícones SVG consistentes |
| **Cards** | capa+tag+título+autor+preço | + rating stars + botão "comprar" visível + badge "novo/destaque" (ref. consenso) |
| **Grid** | auto-fill minmax(230px) | manter, + seção "Destaques" em carrossel horizontal (ref. Leanpub) |
| **Detalhe** | cover+info+buy-box+reviews | + breadcrumb + selos de confiança/garantia + preview (ref. consenso) |
| **Ícones** | mistura emoji + texto | sistema de ícones SVG inline coeso |
| **Footer** | newsletter+3 links+copy | + redes sociais + coluna "Sobre" + selo segurança (ref. 10/10) |
| **Estados vazios** | texto simples | ilustração + CTA para biblioteca/carrinho/favoritos vazios |
| **Loading** | skeleton só no catálogo | loading global + skeleton em detalhe e listas |
| **Erro catálogo** | "Não foi possível carregar" seco | estado de erro com retry + ilustração |

---

## Fases (sequenciamento das 25 tasks)

### Fase 1 — Fundação visual (UXR-01..06)
Tokens de cor expandidos, fonte de display, sistema de ícones SVG, escala de
sombras, gradiente do hero, variáveis de superfície.

### Fase 2 — Header e navegação (UXR-07..10)
Badge de carrinho com contador, ícones SVG no header, menu mobile, avatar/conta.

### Fase 3 — Catálogo e cards (UXR-11..16)
Card redesenhado (rating, CTA compra, badge), seção destaques em carrossel,
estado de erro do catálogo com retry, filtro por preço, estado vazio.

### Fase 4 — Hero e prova social (UXR-17..19)
Hero com CTA + prova social, gradiente, responsividade.

### Fase 5 — Detalhe e footer (UXR-20..24)
Breadcrumb, selos de confiança, footer com redes sociais + colunas, estados vazios
de biblioteca/carrinho.

### Fase 6 — Revisão cíclica (UXR-25)
Parecer de competência, auto-repair, incremento de backlog.

---

## Critérios de aceite do épico

- [ ] Lighthouse (mobile) ≥ 90 em Performance e Accessibility
- [ ] Nenhum dado de marketing hardcoded fora de config
- [ ] Todos os componentes responsivos (mobile/tablet/desktop)
- [ ] Carrinho com contador funcional
- [ ] Estados de erro/vazio desenhados (não texto seco)
- [ ] Identidade roxa preservada + 1 diferencial visual próprio
- [ ] Testes DOM dos novos elementos verdes
