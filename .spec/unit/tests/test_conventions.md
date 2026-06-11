# Unit: test_conventions (`tests`/política)

> Tipo: `tests`/política · Área: `tests`
> Deriva de: [`planning/13`](../../planning/13-estrategia-de-testes.md) · [`standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Padronizar como escrevemos testes (nomes, estrutura, isolamento).

## 2. Localização

| Item | Caminho |
|---|---|
| Política | este doc (referência para todos os testes) |

## 3. Convenções

- **Nome descritivo:** `test_webhook_duplicado_nao_cria_novo_grant`.
- **Arrange / Act / Assert** explícito em cada teste.
- Um cenário Gherkin (seção 6 das units) → um teste.
- Isolamento: sem ordem dependente, sem rede real, tempo controlado.
- Sem comprehension/lambda também nos testes (padrão do projeto).

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `conftest_db`, `conftest_client`, `factories` | base |

## 5. Comportamento / regras

- Cada unit tem seu arquivo de teste correspondente (ver "Localização" das units).
- Testes pequenos e rápidos; E2E à parte.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | Revisão de PR | testes seguem AAA e nomes descritivos |

## 7. Rastreabilidade

- Planning [`13`](../../planning/13-estrategia-de-testes.md) · Standards · Units: todas (cada uma traz seus casos)

## 8. Pendências

- [ ] Lint específico de testes (ex.: `flake8-pytest-style` via Ruff `PT`)?
