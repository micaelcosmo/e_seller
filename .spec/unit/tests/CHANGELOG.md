# CHANGELOG — .spec/unit/tests/

> Histórico específico da trilha de testes.
> **Regra:** este CHANGELOG deve ser atualizado **a cada tarefa** que toque em testes
> (novo guia, nova fixture, nova convenção, novo padrão de mock/segurança/I/O).
> Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

---

## [Não lançado]

### Adicionado — 2026-09-27 (épico QAF — achados do `/qa`)
- Testes de regressão dos achados que só aparecem no **Postgres** (os testes rodam em SQLite):
  `test_qa01_enum_server_default` (DDL de coluna enum), `test_qa02_search_postgres` (SQL da busca
  compilado para o dialeto Postgres — sem `DISTINCT` com `ORDER BY` de relevância),
  `test_qa03_download_timezone` (validade com fuso, como o Postgres devolve), `test_qa16_wishlist_corrida`
  (idempotência do favorito na corrida, forçada com a conferência atrasada).
- Contrato/fluxo: `test_qa04_pedidos_data_e_retomada` (lista do admin com data; pendente com
  `checkout_url`), `test_qa06_cupom_sem_caixa` (cupom sem diferenciar caixa), `test_qa10_painel_admin`
  (login do SQLAdmin com CSRF, contraste sem token, moderação com comentário/status, `/comprar`).
- Lição registrada: teste que "passa" por erro de validação pode esconder quebra real — o
  `test_sec17_csrf` passava porque o CSRF consumia o corpo e o endpoint nem recebia o formulário.
- Teste black-box de ponta a ponta agora é a skill `/qa` (`qa-harness/`, ver `.spec/qa/`).

### Alterado — 2026-06-06 (cobertura dos domínios da visão completa)
- `security_testing.md`: nova seção 3b com cenários de RBAC, review de comprador
  verificado, abuso de cupom, posse única, reemissão de download, estorno revoga
  acesso, consentimento de newsletter (LGPD) e log de download sem IP cru.

### Adicionado — 2026-06-06
- Units de infraestrutura de teste: `pytest_config`, `conftest_db`, `conftest_client`,
  `factories`, `mercadopago_mock`, `time_control`, `coverage_policy`, `e2e_purchase_flow`,
  `test_conventions`.
- **Guias** de testes:
  - `how_to_pytest.md` — estrutura, AAA, fixtures, parametrize, markers, async, ciclo TDD.
  - `mocking_guide.md` — fakes via Protocol, respx, monkeypatch, o que (não) mockar.
  - `security_testing.md` — matriz de segurança (RNF-01/02/03/04/20, auth, JWT, path traversal, LGPD).
  - `io_testing.md` — rotas/status codes, persistência/constraints, streaming, contratos, bordas.
- `CHANGELOG.md` próprio desta pasta.
- `README.md`: seção de guias + **regra de manutenção contínua**.

---

_Início da trilha de testes: 2026-06-06_
