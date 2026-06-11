# 16 — Definition of Done (DoD)

> Documento de planning · e_seller · 2026-06-06
> Critérios objetivos de "pronto". Algo só está concluído se **todos** se aplicarem.

---

## 1. DoD de uma funcionalidade (story/RF)

- [ ] Existe **spec** correspondente (SDD) — em `.spec/`.
- [ ] **Testes escritos antes** (TDD) cobrindo os cenários de aceite e passando.
- [ ] Código segue **PEP 8** (Ruff sem erros).
- [ ] Regras de negócio estão em **services** testáveis (não nos routers).
- [ ] Sem **segredos** no código; configs por variável de ambiente.
- [ ] Roda no ambiente **Docker** (`docker compose up`) sem passos manuais ocultos.
- [ ] **CI verde** (lint + testes + cobertura).
- [ ] Documentação relevante atualizada (README/spec).
- [ ] PR revisado e aprovado.

## 2. DoD de um bugfix

- [ ] Teste que **reproduz** o bug escrito primeiro (falha antes do fix).
- [ ] Fix aplicado; o teste passa.
- [ ] Sem regressão (suíte verde).
- [ ] CHANGELOG atualizado se afetar comportamento observável.

## 3. DoD de um marco / release

- [ ] Todos os itens "Must" do marco com DoD de funcionalidade cumprido.
- [ ] Fluxo crítico testado de ponta a ponta (E2E).
- [ ] **STATUS.md** atualizado.
- [ ] **CHANGELOG.md** (raiz e da pasta afetada) atualizado.
- [ ] Tag/versão criada (quando aplicável).

## 4. DoD do MVP

Ver critérios específicos em [`06-escopo-mvp.md`](06-escopo-mvp.md) §4 — resumidamente:
publicar → comprar → pagar (webhook) → baixar com segurança, com todos os cenários
"Must" verdes.

## 5. O que NÃO conta como "pronto"

- "Funciona na minha máquina" sem Docker/CI.
- Código sem teste "porque é simples".
- Spec desatualizada em relação ao código.
- Segredo commitado "temporariamente".
