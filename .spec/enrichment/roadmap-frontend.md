# Planning Frontend Visual — Enrichment

> Refatoração e enriquecimento visual de todas as views Jinja2. Stack mantida:
> Jinja2 + vanilla JS. Next.js é Tier 2 (bloqueado). Última atualização: 2026-06-13.

---

## Diagnóstico atual

| Aspecto | Estado atual | Objetivo |
|---|---|---|
| CSS | Inline em cada template, variáveis básicas | Design system centralizado, tokens completos |
| Tipografia | system-ui sem escala | Escala modular (1.25), pesos definidos |
| Espaçamento | Ad-hoc (px soltos) | Escala 4px (--space-1..8) |
| Componentes | Botões/cards replicados | Componentes por classe CSS reutilizáveis |
| Feedback | Nenhum (sem toast, sem loading) | Toast + skeleton + spinner |
| Views | 8 templates (básicas) | +4 views novas + todas overhauled |
| Nav | Header simples, sem estado | Dropdown usuário, breadcrumbs, active states |
| Mobile | Responsivo mas sem hamburger | Menu colapsável |
| Forms | Sem validação inline | Erros inline, ARIA labels |
| Acessibilidade | Mínima | ARIA roles, focus-visible, contraste AA |

---

## Design System (tokens CSS)

Arquivo: `backend/app/web/static/css/design-system.css`

```css
:root {
  /* Cores */
  --bg: #0f1226;
  --bg-elevated: #131729;
  --card: #1a1f3a;
  --card-hover: #1f2545;
  --border: #2a2f55;
  --border-focus: #7c5cff;
  --ink: #eef;
  --ink-muted: #9aa;
  --ink-subtle: #667;
  --accent: #7c5cff;
  --accent-hover: #6b4de8;
  --accent-dim: #7c5cff22;
  --success: #22c55e;
  --danger: #ef4444;
  --warning: #f59e0b;
  --info: #3b82f6;

  /* Tipografia */
  --font-sans: system-ui, "Segoe UI", Roboto, sans-serif;
  --font-mono: "Cascadia Code", "Fira Code", monospace;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --fw-normal: 400;
  --fw-medium: 500;
  --fw-semibold: 600;
  --fw-bold: 700;
  --fw-extrabold: 800;
  --lh-tight: 1.25;
  --lh-base: 1.5;

  /* Espaçamento (base 4px) */
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-5: 1.25rem;  /* 20px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-10: 2.5rem;  /* 40px */
  --space-12: 3rem;    /* 48px */

  /* Raios */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-full: 9999px;

  /* Sombras */
  --shadow-sm: 0 1px 3px #0004;
  --shadow-md: 0 4px 12px #0006;
  --shadow-lg: 0 8px 24px #0008;

  /* Transições */
  --transition-fast: 120ms ease;
  --transition-base: 200ms ease;
}
```

---

## Componentes Base

### Botões
```css
.btn { /* base */ }
.btn-primary { background: var(--accent); }
.btn-ghost { background: var(--border); }
.btn-danger { background: var(--danger); }
.btn-sm { padding: var(--space-2) var(--space-3); font-size: var(--text-sm); }
.btn-lg { padding: var(--space-4) var(--space-6); font-size: var(--text-lg); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn.loading { position: relative; /* spinner overlay */ }
```

### Cards
```css
.card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-lg); }
.card-hover:hover { background: var(--card-hover); border-color: var(--accent-dim); }
.card-body { padding: var(--space-4); }
.card-cover { /* imagem de capa */ aspect-ratio: 3/4; object-fit: cover; border-radius: var(--radius-md) var(--radius-md) 0 0; }
```

### Toast
```javascript
// toast.js (inline no base.html)
class Toast {
  show(message, type = 'info') { /* cria div, anima, remove após 4s */ }
  success(msg) { this.show(msg, 'success'); }
  error(msg) { this.show(msg, 'error'); }
  info(msg) { this.show(msg, 'info'); }
}
window._toast = new Toast();
```

### Loading / Skeleton
```html
<div class="skeleton" aria-busy="true" aria-label="Carregando..."></div>
```

---

## Views a overhauled

### 1. base.html — Refatoração completa
- Header: logo + nav links + dropdown usuário autenticado (JS)
- Footer: 3 colunas (links, newsletter inline, social)
- CSS: importa design-system.css; remove inline
- Toast container: `<div id="toast-root"></div>`
- Loading overlay: `<div id="loading-overlay" hidden></div>`

### 2. index.html — Catálogo
- Hero section: headline + search bar grande
- Grid: cards com cover image, título, autor, preço, tag "destaque"
- Sidebar: filtros por categoria/tag/autor (chips)
- Paginação: redesenhada (numbers + prev/next)
- Empty state: ilustração quando sem resultados

### 3. produto_detalhe.html — Detalhe do e-book
- Layout 2 colunas: capa (esq) + info + CTA (dir)
- Preço com badge de desconto quando coupon ativo
- Botão "Comprar" → loading state → toast de feedback
- Seção reviews: rating stars, avatar inicial, paginação
- Related products (carrossel simples)

### 4. order.html — Status do pedido
- Timeline visual de status (pending → paid → delivered)
- Cards de download com botão + contador (X de Y restantes)
- Badge de status colorido
- CTA "Ir para Biblioteca" quando entregue

### 5. recuperar_senha.html — Senha
- Stepper visual (solicitar → verificar → redefinir)
- Validação inline: força da senha, confirmação
- Feedback visual em cada step

### 6. conta.html — Perfil (NOVA VIEW)
- Hash `#/conta` → renderização SPA inline
- Tabs: Dados pessoais / Dados de faturamento / Segurança / Atividade
- Formulário billing_profile com CPF/CNPJ mask
- Lista de atividades recentes (GET /me/activity)
- Botão de logout com confirmação

### 7. biblioteca.html — Minha Biblioteca (NOVA VIEW)
- `#/biblioteca` → lista entitlements do usuário
- Cards de e-book com links de download ativos/expirados
- Indicador de downloads restantes / expiração
- Redownload via grant reemissão

### 8. carrinho.html — Carrinho (NOVA VIEW)
- `#/carrinho` → lista CartItems
- CRUD de itens, subtotal, campo de cupom
- Botão checkout → redirect para MP

### 9. favoritos.html — Wishlist (NOVA VIEW)
- `#/favoritos` → lista WishlistItems
- Grid de cards, botão "Comprar" + "Remover"

### 10. terms.html / privacy.html — Legal
- Typography enriquecida (heading hierarchy, line-height, max-width)
- Índice lateral (links internos)
- Dark mode correto (sem texto branco sobre branco)

### 11. simulate.html — Simulador de pagamento
- Layout mais limpo; botões de ação destacados
- Status visual do webhook

### 12. Admin HTML pages — Relatórios
- Orders dashboard: tabela com sorting, filtros visuais
- Downloads dashboard: gráfico simples (SVG inline)
- Cards de métricas (KPIs)

### 13. Error pages (404, 500) — NOVAS
- Design consistente com o tema
- Botão "Voltar ao início"

---

## Navegação e SPA inline

Padrão atual: `#/rota` → JS intercepta e renderiza via fetch + innerHTML.

Novas rotas:
- `#/` → catálogo
- `#/conta` → perfil
- `#/biblioteca` → biblioteca
- `#/carrinho` → carrinho
- `#/favoritos` → favoritos
- `#/pedido/{ref}` → status do pedido

Nav bar deve ter links para rotas autenticadas (mostrar/esconder via JS baseado em token).

---

## Acessibilidade

- `aria-label` em todos os inputs
- `role="alert"` em toast
- `aria-busy` em loading states
- `focus-visible` outline visível (`:focus-visible { outline: 2px solid var(--accent); }`)
- Contraste WCAG AA verificado (roxo #7c5cff sobre escuro #0f1226 ≈ 5.6:1 ✅)

---

## Definition of Done

- [ ] Design system CSS extraído para arquivo estático
- [ ] Todos os 8 templates existentes overhauled
- [ ] 4 novas views implementadas
- [ ] Toast + loading funcionando
- [ ] Nav com estado autenticado
- [ ] Mobile nav colapsável
- [ ] Forms com validação inline
- [ ] ARIA labels nos elementos críticos
- [ ] Testes HTML (pytest verifica presença de elementos-chave)
- [ ] Ruff limpo (Python; JS não tem linter)
