# .spec/planning/

Fase de **planejamento** do e_seller (portal de vendas de e-books).
Trabalhamos **exclusivamente** aqui até o planning estar completo e aprovado.

> Metodologia geral em [`../../CLAUDE.md`](../../CLAUDE.md): Spec-Driven Development,
> Test-Driven Development e PEP 8.

## Convenções desta pasta

- Documentos numerados por ordem lógica de leitura (`NN-nome.md`).
- Toda alteração relevante nesta pasta é registrada em [`CHANGELOG.md`](CHANGELOG.md).
- Datas absolutas (`AAAA-MM-DD`).

## Índice de documentos

### Grupo A — Discovery & Produto
- [`01-visao-de-produto.md`](01-visao-de-produto.md) — problema, proposta de valor, objetivos e métricas.
- [`02-personas-e-jornadas.md`](02-personas-e-jornadas.md) — quem usa e como percorre o produto.
- [`03-requisitos-funcionais.md`](03-requisitos-funcionais.md) — o que o sistema deve fazer (RF).
- [`04-requisitos-nao-funcionais.md`](04-requisitos-nao-funcionais.md) — qualidades e restrições (RNF).
- [`05-user-stories.md`](05-user-stories.md) — histórias com critérios de aceite (base do TDD).
- [`06-escopo-mvp.md`](06-escopo-mvp.md) — o que entra e o que fica de fora no MVP.

### Grupo B — Arquitetura & Técnico
- [`07-adr-stack.md`](07-adr-stack.md) — decisão de stack registrada (ADR).
- [`08-arquitetura.md`](08-arquitetura.md) — visão de componentes e fluxos.
- [`09-modelo-de-dominio.md`](09-modelo-de-dominio.md) — entidades e regras de negócio.
- [`10-modelo-de-dados.md`](10-modelo-de-dados.md) — modelo relacional (ER) e mapeamento SQLAlchemy/Alembic.
- [`11-contratos-api.md`](11-contratos-api.md) — endpoints/contratos internos.
- [`12-docker-e-ambientes.md`](12-docker-e-ambientes.md) — containers, ambientes e configuração.

### Grupo C — Qualidade & Processo
- [`13-estrategia-de-testes.md`](13-estrategia-de-testes.md) — pirâmide de testes e prática de TDD.
- [`14-padroes-de-codigo.md`](14-padroes-de-codigo.md) — PEP 8, Ruff, type hints, convenções.
- [`15-ci-cd.md`](15-ci-cd.md) — pipeline de integração e entrega.
- [`16-definition-of-done.md`](16-definition-of-done.md) — critérios de "pronto".
- [`17-fluxo-sdd.md`](17-fluxo-sdd.md) — como Spec → Teste → Código opera na prática.

### Grupo D — Negócio & Operação
- [`18-pagamentos-mercado-pago.md`](18-pagamentos-mercado-pago.md) — integração de pagamento.
- [`19-seguranca-e-lgpd.md`](19-seguranca-e-lgpd.md) — segurança e proteção de dados.
- [`20-entrega-ebook-anti-pirataria.md`](20-entrega-ebook-anti-pirataria.md) — entrega segura do arquivo.
- [`21-roadmap.md`](21-roadmap.md) — marcos e sequência de entrega.
- [`22-matriz-de-riscos.md`](22-matriz-de-riscos.md) — riscos, impacto e mitigação.

## Status

Em produção (escrita) — ver [`CHANGELOG.md`](CHANGELOG.md) e [`../../STATUS.md`](../../STATUS.md).
