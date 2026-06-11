# CHANGELOG — .spec/unit/tests/

> Histórico específico da trilha de testes.
> **Regra:** este CHANGELOG deve ser atualizado **a cada tarefa** que toque em testes
> (novo guia, nova fixture, nova convenção, novo padrão de mock/segurança/I/O).
> Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

---

## [Não lançado]

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
