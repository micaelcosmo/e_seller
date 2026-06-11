# Convenções do Frontend

> Trilha frontend · e_seller · 2026-06-07
> Análogo aos [`../standards/`](../standards/) do backend, adaptado a TS/React.

---

## 1. Idioma e encoding

- **Código em inglês**; **comentários/JSDoc em pt-BR** (mesma regra do backend — evita encode/decode).
- Arquivos em **UTF-8**.
- **Toda função/componente/hook com comentário/JSDoc** explicando o propósito (pt-BR).

## 2. TypeScript

- `strict: true`. Tipos vindos do **OpenAPI** para dados da API.
- Sem `any` implícito.

## 3. Estrutura (proposta)

```
frontend/
├─ app/                 # rotas (Next.js App Router)
├─ components/          # componentes reutilizáveis
├─ features/            # por domínio (catalog, orders, library, dashboard)
├─ lib/api/             # client gerado do OpenAPI + wrappers
├─ lib/                 # utilidades
└─ tests/               # Vitest + Testing Library
```

## 4. Componentes

- **Componentes funcionais** + hooks; um componente por arquivo.
- Lógica de dados em **hooks/serviços** (`features/<dominio>/`), não dentro do JSX.
- Nomes declarativos (`ProductCard`, não `PCard`).

## 5. Qualidade

- **ESLint + Prettier** (equivalente ao Ruff); CI roda lint + testes.
- Testes de componente (Vitest/Testing Library) para comportamento, não detalhes.

## 6. Acessibilidade & responsivo

- Semântica HTML, navegação por teclado, contraste; responsivo (RNF-50).

## 7. Pendências

- [ ] Tailwind vs CSS Modules; convenções de estilo.
- [ ] Regras de ESLint específicas.
