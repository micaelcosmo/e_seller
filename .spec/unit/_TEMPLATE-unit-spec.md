# Unit: <nome-do-componente> (`<tipo>`)

> Tipo: `model` | `schema` | `service` | `router` | `gateway` | `dependency` |
> `migration` | `config` | `fixture` | `infra` · etc.
> Área: `<backend/<módulo>` | `db` | `security` | `infra` | `tests>`
> Deriva de: `<RF/RNF, US, e docs de planning>` · Status: **Rascunho**
> Padrões: segue [`../standards/`](../standards/) — services = **classe com DI no `__init__`**,
> POO, sem globais, sem comprehension/lambda, naming declarativo.

---

## 1. Objetivo

Uma frase: o que esta unidade faz e por que existe.

## 2. Localização (proposta)

| Item | Caminho |
|---|---|
| Código | `backend/app/<módulo>/<arquivo>.py::<símbolo>` |
| Teste | `backend/tests/<módulo>/test_<nome>.py` |

## 3. Contrato (assinatura)

> Services = **classe** com dependências injetadas no `__init__` (SOLID/DIP).
> Models/schemas/utilitários seguem a forma adequada ao tipo.

```python
# Service (exemplo de forma — classe com DI)
class <NomeDoService>:
    def __init__(self, <dependencias>) -> None:
        self.<dep> = <dep>          # atributos via self. no __init__

    def <metodo>(self, <args>) -> <retorno>:
        ...
# Levanta: <Exceções> em <condições>
```

- **Entrada:** ...
- **Saída:** ...
- **Erros/Exceções:** ...
- **Dependências do `__init__`:** ... (injetadas, nunca instanciadas por dentro)

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `<outra unit/serviço>` | ... | real / **mock** |

> Liste o que será **mockado** (ex.: gateway externo) e o que será real (ex.: DB de teste).

## 5. Comportamento / regras

- Regra/invariante 1 (referência ao planning, ex.: [`09-modelo-de-dominio`](../../planning/09-modelo-de-dominio.md)).
- Efeitos colaterais (persistência, eventos).
- Pré-condições e pós-condições.

## 6. Casos de teste (TDD) — escrever o **Red** primeiro

> Cada caso vira um teste. Cobrir: caminho feliz, erros, bordas e idempotência quando aplicável.

| # | Cenário (Gherkin curto) | Entrada | Resultado esperado |
|---|---|---|---|
| T1 | Dado … Quando … Então … | ... | ... |
| T2 | (erro) … | ... | exceção/erro X |
| T3 | (borda) … | ... | ... |

## 7. Rastreabilidade

- **Requisitos:** RF-xx, RNF-xx
- **User stories:** US-xx
- **Planning:** [`<doc>`](../../planning/<doc>.md)
- **Units relacionadas:** `<área>/<unit>`

## 8. Pendências / decisões

- [ ] ...
