# Docstrings e Idioma

> Padrão · e_seller · 2026-06-07 · **obrigatório**

---

## 1. Idioma do código vs. documentação

- **Código em inglês:** identificadores (classes, métodos, variáveis, módulos) em inglês
  (convenção do ecossistema Python/FastAPI).
- **Comentários e docstrings em Português-BR — obrigatório.**

> 💡 **Por quê separar?** Evita problemas de **encode/decode**: o código (ASCII em
> inglês) fica livre de acentuação; o texto humano (pt-BR, com acentos) fica isolado
> em comentários/docstrings, sempre em arquivos **UTF-8**.

```python
class WebhookProcessor:
    """Processa notificações de pagamento de forma idempotente."""

    def process(self, notification: WebhookNotification) -> WebhookResult:
        """Confirma o pagamento na fonte e libera a entrega se aprovado."""
        ...
```

## 2. Docstring obrigatória em TODA funcionalidade

- **Toda** classe, método e função tem docstring (sem exceção).
- A docstring diz o **porquê/contrato** (o que faz, o que recebe/retorna, o que levanta),
  não repete o óbvio do nome.
- Métodos triviais (ex.: getters) ainda têm uma docstring curta de uma linha.
- Estilo: pt-BR, imperativo/descritivo curto; documentar parâmetros/erros relevantes.

### Mínimo aceitável
```python
def total(self) -> Decimal:
    """Retorna a soma dos preços atuais dos itens do carrinho."""
    ...
```

## 3. Codificação de arquivos

- Todos os arquivos `.py` em **UTF-8** (sem BOM).
- Sem caracteres acentuados em identificadores.

## 4. Enforcement

- Docstring ausente → reprovado na revisão. Pode ser apoiado pelo Ruff
  (regras `D` / pydocstyle) — avaliar habilitar em [`python-and-tooling.md`](python-and-tooling.md).
- Acentuação em identificadores → revisão.

## 5. Relacionado

[`oop-and-naming.md`](oop-and-naming.md) (estrutura POO) · [`enforcement.md`](enforcement.md).
