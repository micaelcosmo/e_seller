# UX Audit — Storefront e_seller (estado atual)

> Documento de referência para o épico UXR (UX Redesign).
> Descreve o que existe hoje, o que funciona, o que precisa mudar.
> Atualizado: 2026-06-13

---

## 1. Stack e arquitetura frontend

- **Tipo:** SPA vanilla JS (sem framework) servido por Nginx no Docker
- **Arquivos:** `index.html` + `style.css` + `app.js`
- **Roteamento:** hash-based (`#/`, `#/produto/slug`, `#/conta`, etc.)
- **API:** REST FastAPI em `/api/*` (mesmo domínio, proxiado pelo Nginx)
- **Autenticação:** JWT no `localStorage`; botões condicionados ao role

---

## 2. Paleta de cores atual

| Token | Valor | Uso |
|---|---|---|
| `--bg` | `#f6f7fb` | Fundo da página |
| `--ink` | `#1a1d2b` | Texto principal |
| `--muted` | `#6b7280` | Texto secundário, labels |
| `--card` | `#ffffff` | Cards, header, footer |
| `--line` | `#e6e8f0` | Bordas, divisores |
| `--accent` | `#6d5cff` | CTA, links, active states |
| `--accent-ink` | `#ffffff` | Texto sobre accent |
| `--ok` | `#15a05a` | Sucesso, badge comprado |
| erro | `#d3455b` | Erros, toast vermelho |

**Avaliação:** paleta coerente e limpa. Accent roxo-azulado funciona bem. Problema: sem variação de profundidade — tudo parece "flat". Ausência de tons intermediários entre `--bg` (#f6f7fb) e `--card` (#fff).

---

## 3. Tipografia atual

- **Família:** `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`
- **Tamanho base:** implícito 16px
- **Hero H1:** `clamp(1.8rem, 4vw, 2.8rem)` — responsivo
- **Card H3:** `1rem`
- **Preço:** `1.1rem`, `font-weight: 800`
- **Muted/tag:** `0.72rem – 0.85rem`

**Avaliação:** sem fonte de display — o hero usa system font, ficando genérico. Hierarquia razoável mas sem personalidade. Ausência de `font-display: swap` (performance em custom fonts).

---

## 4. Componentes existentes

### Header/Topbar
- Logo (emoji 📚 + texto), busca central pill, ações à direita
- Sticky, `z-index: 5`
- Botões: ghost com borda; admin link oculto por JWT role
- **Faltando:** indicador de itens no carrinho (badge numérico), avatar do usuário

### Hero
- H1 + subtítulo, centralizado, padding `48px 20px 8px`
- **Faltando:** CTA secundário ("Ver catálogo"), nenhuma imagem/ilustração

### Grid de Produtos
- `auto-fill, minmax(230px, 1fr)`, gap 18px
- Cards com: cover (aspect 3/4), tag de categoria, título, autor, preço
- Hover: `translateY(-3px)` + sombra mais profunda
- Skeleton loader animado (shimmer)
- **Faltando:** rating stars nos cards, badge "Novo", badge "Mais vendido"

### Cards
- `border-radius: 14px`, sombra suave
- Cover placeholder: iniciais + HSL hash (implementado em SFX-05)
- **Faltando:** botão "Adicionar ao carrinho" visível sem clicar, preço em destaque maior

### Filtros/Facetas
- Chips por tag/categoria na barra de facetas
- Sort bar (select nativo)
- **Faltando:** filtro por faixa de preço, filtro por formato, busca em tempo real (debounce existe mas UX fraca)

### Página de Detalhe
- Grid 2 colunas (cover + info), buy-box com border
- Reviews com estrelas
- "Você também pode gostar" (related)
- **Faltando:** breadcrumb, preview do e-book, lista de capítulos/conteúdo, garantia/selos de confiança

### Autenticação
- Modal (login/registro), sem OAuth
- **Faltando:** "Esqueci minha senha", feedback de força de senha, persistência de sessão (30 dias)

### Biblioteca
- Lista dos e-books comprados com botão download
- **Faltando:** progresso de leitura, organização por coleção

### Carrinho
- **Estado:** implementado mas sem indicador visual no header

### Footer
- Newsletter (inline form), links (Privacidade · Termos · API), copyright
- **Faltando:** redes sociais, "Sobre nós", selo SSL/segurança, mapa do site

---

## 5. Responsividade

- `@media (max-width: 640px)`: detalhe vai para 1 coluna, busca quebra linha
- Grid usa `auto-fill` — adapta bem
- **Faltando:** breakpoint tablet (768px), menu hamburguer no mobile, cards menores no mobile (minmax 160px?)

---

## 6. Performance / Acessibilidade

- `aria-label`, `role="alert"`, `aria-live` presentes nos elementos críticos
- Skeleton loader com shimmer — bom
- `theme-color` meta tag — bom
- **Faltando:** `<meta og:image>`, favicon real, `lang` correto (tem), `preconnect` para fontes externas (não usa ainda), lighthouse score desconhecido

---

## 7. Identidade visual

- Sem logo real (emoji 📚)
- Sem favicon dedicado
- Sem paleta secundária
- Sem ilustrações ou ícones consistentes (mistura emoji + texto)
- **Conclusão:** funcional, sem personalidade de marca

---

## 8. O que funciona bem (manter)

1. Paleta de cores coerente com tokens CSS
2. Skeleton loader com shimmer
3. Grid responsivo com `auto-fill`
4. Cards com hover sutil
5. Modal de auth com tabs login/registro
6. Toast system (exceto newsletter — já corrigido)
7. Cover placeholder com iniciais + HSL (SFX-05)
8. Admin link condicionado por JWT role (SFX-03)
9. Footer unificado sem duplicata (SFX-01)

---

## 9. Problemas críticos (corrigir no UXR)

| Prioridade | Problema |
|---|---|
| 🔴 Alta | Hero sem CTA clicável — usuário fica perdido se catálogo falha |
| 🔴 Alta | Botão "Adicionar ao carrinho" não visível no card (só no detalhe) |
| 🔴 Alta | Badge numérico no ícone do carrinho ausente |
| 🔴 Alta | Sem loading state global (só skeleton no catálogo) |
| 🟡 Média | Sistema de ícones inconsistente (emoji vs texto) |
| 🟡 Média | Tipografia sem fonte de display — hero genérico |
| 🟡 Média | Página de detalhe sem selos de confiança/garantia |
| 🟡 Média | Sem estado "vazio" desenhado para biblioteca/carrinho |
| 🟢 Baixa | Footer sem redes sociais |
| 🟢 Baixa | Sem favicon real |
| 🟢 Baixa | Sem `og:image` |
