# Barra de Qualidade — e_seller (norte do "pronto")

> Documento **vivo**. Define o que é "bom o suficiente" no objetivo final:
> **um site de venda de e-books — funcional, leve e bem feito.**
> Referenciado pela [revisão cíclica](self_reflection/cyclic-review.md).

---

## 0. Princípio inegociável — NÃO sair do contexto

Tudo que for feito serve **somente** ao objetivo: **vender e-books** (catálogo →
compra → pagamento → entrega segura) com boas práticas. Itens que **não** servem a
isso são rejeitados na revisão cíclica (anti-scope-creep). O e-book é o **único**
tipo de produto.

## 1. Backend (POO, sem amarras)

- **POO de verdade:** classes coesas, injeção de dependência, sem variáveis globais.
- **Camadas:** `router` (HTTP) → `service` (regra) → `repository/model` (dados);
  **nenhuma regra de negócio no router**.
- **Sem amarras:** código desacoplado (Protocols nas fronteiras), trocável e testável;
  sem dependência rígida de detalhes (DIP).
- Docstrings pt-BR em tudo; sem comprehension/lambda; type hints.
- Erros tratados de forma padronizada (exception handlers → HTTP coerente).

## 2. Banco de dados (organização, observabilidade, relacionamento determinístico)

- **Relacionamentos determinísticos:** FKs explícitas, cardinalidades claras,
  tabelas de associação para N:N, `ON DELETE` pensado (proteger histórico).
- **Integridade:** UNIQUE/CHECK no banco (não só na aplicação) — ex.: `provider_payment_id`,
  `entitlement(user,product)`, `price >= 0`.
- **Tipos corretos:** `Numeric` p/ dinheiro, `timestamptz`, `uuid`, `jsonb`.
- **Observabilidade:** migrations versionadas (Alembic) + **UML atualizada a cada migração**;
  índices por consulta; (prod) log de slow query e métricas de conexão.
- **Organização:** nomes declarativos; seeds determinísticos; retenção LGPD no schema.

## 3. Frontend (UX correta e leve)

- **Layout certo:** centralização/alinhamento com **flexbox/grid** (nada de gambiarra
  de margin/`position` pra "centralizar"); espaçamento consistente.
- **Sem recarregar a página:** carregar/atualizar itens via **fetch/AJAX** (loading
  states, skeletons), navegação fluida (SPA/SSR do Next).
- **Tooltips/hints sugestivos** nos pontos de dúvida (ícones, campos, ações).
- **Feedback claro:** toasts de sucesso/erro; estados de vazio e de carregamento.
- **Acessibilidade:** semântica, navegação por teclado, `aria-*`, contraste.
- **Leve:** code splitting, imagens otimizadas, pouco JS; responsivo (mobile-first).
- **Validação dupla:** client-side (UX) + server-side (verdade).

## 4. Transversal

- **Funcional acima de tudo:** o fluxo de valor funciona ponta a ponta e tem teste.
- **Leve:** sem dependências/abstrações desnecessárias.
- **Testado:** cobertura ≥ 95% nos módulos de domínio; segurança testada.
- **🚫 SEM DADOS EM HARDCODE:** nenhum valor "chumbado" no código —
  - segredos/credenciais/URLs/portas → **variáveis de ambiente** (`Settings`);
  - parâmetros de negócio (limites, prazos, preços de exemplo) → **config/DB**, não literais;
  - dados de catálogo/seed → **externalizados** (arquivo de dados/DB), não embutidos no código;
  - constantes legítimas (ex.: mapa de status do provedor) ficam como **constantes nomeadas**,
    não espalhadas como literais mágicos.
- Cada entrega passa pela [revisão cíclica](self_reflection/cyclic-review.md).
