# ADR Frontend: Stack

> Trilha frontend · e_seller · 2026-06-07 · Status: **Aceito**

---

## ADR-F1 — Storefront em Next.js (React, SSR)

- **Contexto:** loja de e-books; páginas de produto precisam de **SEO** (serem
  indexáveis) para atrair vendas; backend é API separada.
- **Decisão:** **Next.js** (React + TypeScript), com **SSR/SSG** nas páginas de catálogo/produto.
- **Consequências:**
  - ✅ SEO em páginas de produto; boa performance percebida.
  - ✅ React tem ecossistema enorme; TypeScript dá segurança de tipos.
  - ✅ Pode **gerar client** a partir do OpenAPI ([`../api/openapi-workflow.md`](../api/openapi-workflow.md)).
  - ⚠️ Mais complexo que SPA pura; exige Node no container do frontend.

## ADR-F2 — Dashboard UI na mesma stack + gráficos

- **Decisão:** a UI do [dashboard de evolução](../dashboard/) usa a **mesma stack**
  (Next.js/React + TypeScript) com biblioteca de gráficos **Recharts** (ou Chart.js).
- **Consequências:**
  - ✅ Um ecossistema só; consistência e reaproveitamento.
  - ✅ Lê `dashboard.json` (ou `GET /dashboard/data`) e renderiza os gráficos.

## ADR-F3 — TypeScript + Tooling

- **Decisão:** **TypeScript**, **ESLint + Prettier** (equivalente ao Ruff no backend),
  **Vitest/Testing Library** para testes de componente.
- **Consequências:** padrão de qualidade análogo ao do backend (lint + testes no CI).

## Decisões em aberto

- [ ] Recharts vs Chart.js.
- [ ] Biblioteca de UI/estilo (Tailwind? CSS Modules?).
- [ ] Gerenciamento de estado (Context/Zustand) — provavelmente mínimo no início.
- [ ] Um app Next com duas áreas (loja + /dashboard) vs dois apps separados.
