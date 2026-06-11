# Referências de Design (inspiração)

> Trilha frontend · e_seller · 2026-06-07
> Referências passadas pelo Micael. **Norte principal: Sellfy** ("gostei desse").

---

## 1. Norte: Sellfy

**Por que:** Sellfy é uma plataforma enxuta de venda de produtos digitais (e-books
inclusos): storefront **limpo e moderno**, **criação de produto rápida**, **entrega
digital instantânea**, foco no **criador** (não em marketplace gigante).

**Princípios a adotar (do Sellfy):**
- Loja **minimalista**, visual moderno, CTA claro de compra.
- **Cadastro de produto simples e direto** (combina com nosso cadastro dinâmico:
  JSON / link / manual — ver [`../unit/backend/catalog/service_create_product.md`](../unit/backend/catalog/service_create_product.md)).
- Checkout curto; **entrega imediata** após pagamento (já é o nosso fluxo).
- Página de produto enxuta: capa, título, autor, preço, descrição, botão comprar.

## 2. Demais referências (e o que aproveitar)

| Referência | O que observar |
|---|---|
| Sellfy (★) | Simplicidade de loja e de cadastro de produto; foco no criador. |
| UICLAP (loja.uiclap.com) | Loja de e-book BR: página de título, preço, formatos. |
| Amazon KDP | Fluxo de publicação de e-book (metadados, formatos, preço). |
| Apple Books | Apresentação premium da página de produto. |
| Smashwords | Distribuição/multiformato de e-books. |
| Kobo Writing Life | Painel do autor (publicação/relatórios). |
| Hotmart | Checkout BR, área de membros, entrega digital. |
| Clube de Autores (BR) | Publicação independente, foco BR. |
| PublishDrive | Catálogo/distribuição multicanal. |
| B&N Press | Página de produto/editorial. |

## 3. Como mapeia no e_seller

- **Home/landing:** destaque de e-books + proposta clara (estilo Sellfy).
- **Página do e-book:** capa, autor, preço, descrição, "Comprar" — enxuta (Apple/Sellfy).
- **Admin de produto:** cadastro **rápido e dinâmico** (Sellfy/KDP) — JSON/link/manual.
- **Pós-compra:** download imediato + "Minha Biblioteca" (Hotmart/Kobo).

## 4. Pendências

- [ ] Definir paleta/tipografia e design system mínimo (Tailwind?) inspirado no Sellfy.
- [ ] Wireframes das telas principais (home, produto, checkout, admin-cadastro).
