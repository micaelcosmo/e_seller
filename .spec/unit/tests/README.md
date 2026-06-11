# unit/tests/

Trilha de **testes** do e_seller (TDD), derivada de
[`../../planning/13-estrategia-de-testes.md`](../../planning/13-estrategia-de-testes.md)
e dos [`../../standards/`](../../standards/). Aqui especificamos *como* testamos
(pytest, mock, segurança, I/O); os casos de teste de cada componente vivem na própria
unit (seção 6 do template).

> ✅ Units e guias gerados (2026-06-06). Histórico em [`CHANGELOG.md`](CHANGELOG.md).

---

## ⚠️ Regra de manutenção contínua

**Esta pasta é viva e deve ser atualizada a cada tarefa** que envolva testes:
ao criar/alterar fixtures, convenções, padrões de mock, casos de segurança ou de I/O,
**atualize o guia correspondente e registre no [`CHANGELOG.md`](CHANGELOG.md)**.
Specs de teste e prática real nunca devem divergir.

---

## Guias (como testar)

| Guia | Assunto |
|---|---|
| [`how_to_pytest.md`](how_to_pytest.md) | Estrutura, AAA, fixtures, parametrize, markers, async, ciclo TDD. |
| [`mocking_guide.md`](mocking_guide.md) | Fakes via Protocol, respx, monkeypatch, o que (não) mockar. |
| [`security_testing.md`](security_testing.md) | Matriz de segurança: RNF-01/02/03/04/20, auth/JWT, path traversal, LGPD. |
| [`io_testing.md`](io_testing.md) | Rotas/status codes, persistência/constraints, streaming, contratos, bordas. |

## Units (ferramental de teste)

| Unit | Papel |
|---|---|
| [`pytest_config.md`](pytest_config.md) | `pytest`/`pytest-asyncio`/`pytest-cov` no `pyproject.toml`. |
| [`conftest_db.md`](conftest_db.md) | Sessão SQLAlchemy de teste (rollback por teste). |
| [`conftest_client.md`](conftest_client.md) | Client `httpx` sobre o app ASGI (sem rede). |
| [`factories.md`](factories.md) | `factory_boy` para os models. |
| [`mercadopago_mock.md`](mercadopago_mock.md) | Fake do gateway / mock HTTP (`respx`). |
| [`time_control.md`](time_control.md) | Tempo determinístico (`Clock`/`freezegun`). |
| [`coverage_policy.md`](coverage_policy.md) | Política e gate de cobertura no CI. |
| [`e2e_purchase_flow.md`](e2e_purchase_flow.md) | E2E do fluxo crítico. |
| [`test_conventions.md`](test_conventions.md) | Nomeação, AAA, isolamento. |

> 💡 Cada unit de `backend/`, `db/` e `security/` traz seus **próprios casos de teste**;
> estas units e guias definem o **ferramental e o método** que os tornam consistentes.
