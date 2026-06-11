# CHANGELOG — .spec/planning/

> Histórico específico da pasta de planning.
> Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
> Datas no formato `AAAA-MM-DD`.

---

## [Não lançado]

### Adicionado
- `README.md`: índice e convenções da pasta de planning.
- `CHANGELOG.md`: este arquivo.
- **Grupo A — Discovery & Produto:** `01-visao-de-produto`, `02-personas-e-jornadas`,
  `03-requisitos-funcionais`, `04-requisitos-nao-funcionais`, `05-user-stories`, `06-escopo-mvp`.
- **Grupo B — Arquitetura & Técnico:** `07-adr-stack`, `08-arquitetura`,
  `09-modelo-de-dominio`, `10-modelo-de-dados`, `11-contratos-api`, `12-docker-e-ambientes`.
- **Grupo C — Qualidade & Processo:** `13-estrategia-de-testes`, `14-padroes-de-codigo`,
  `15-ci-cd`, `16-definition-of-done`, `17-fluxo-sdd`.
- **Grupo D — Negócio & Operação:** `18-pagamentos-mercado-pago`, `19-seguranca-e-lgpd`,
  `20-entrega-ebook-anti-pirataria`, `21-roadmap`, `22-matriz-de-riscos`.

### Decisões registradas
- Backend Django + Python 3.14.5+; PostgreSQL; Mercado Pago; Docker em todos os serviços;
  custo inicial zero; frontend a decidir (backend API-first).

### Alterado — 2026-06-06 (revisão de stack)
- **Backend migrado de Django para FastAPI**; **backend e frontend separados**
  (serviços independentes).
- Acréscimos: **SQLAlchemy 2.x + Alembic** (ORM/migrations), **SQLAdmin** (painel
  admin, no lugar do Django Admin), **OAuth2 + JWT** (auth), **API JSON** com
  **OpenAPI/Swagger automático**, **Uvicorn/Gunicorn**.
- Mantidos: PostgreSQL, Mercado Pago, Docker, custo zero, metodologia SDD/TDD/PEP 8.
- Documentos revisados: 01, 02, 03, 06, 07, 08, 10, 11, 12, 13, 14, 15, 16, 17, 18,
  19, 21, 22 e o `README.md` (índice).

---

_Início do planning: 2026-06-06_
