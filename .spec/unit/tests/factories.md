# Unit: factories (`tests`)

> Tipo: `fixture`/factories · Área: `tests`
> Deriva de: [`planning/13`](../../planning/13-estrategia-de-testes.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Factories (`factory_boy`) para criar dados de teste legíveis e consistentes.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/tests/factories.py` |

## 3. Contrato

```python
class ProductFactory(SQLAlchemyModelFactory): ...
class OrderFactory(SQLAlchemyModelFactory): ...
class PaymentFactory(SQLAlchemyModelFactory): ...
class DownloadGrantFactory(SQLAlchemyModelFactory): ...
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `factory_boy` | construção |
| `conftest_db` (sessão) | persistir |
| models | alvo |

## 5. Comportamento / regras

- Defaults sensatos; sobrescrevíveis por teste.
- Nomes declarativos; sem lambda/comprehension nas definições auxiliares.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | `ProductFactory()` | cria produto válido |
| T2 | Override de campo | respeita o valor passado |

## 7. Rastreabilidade

- Planning [`13`](../../planning/13-estrategia-de-testes.md) · Units: models, `conftest_db`

## 8. Pendências

- [ ] factory_boy vs fixtures simples (decidir).
