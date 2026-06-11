# POO e Nomenclatura

> Padrão · e_seller · 2026-06-06

---

## 1. Pense em POO

- Modelar comportamento em **classes** coesas; estado encapsulado.
- **Sem variáveis globais** e sem estado mutável de módulo. Configuração vem de um
  objeto `Settings` **injetado**, não de globais.
- Atributos definidos no **`__init__`** via `self.`:
  ```python
  class DownloadIssuer:
      def __init__(self, session: Session, max_downloads: int, ttl_days: int) -> None:
          self.session = session
          self.max_downloads = max_downloads
          self.ttl_days = ttl_days
  ```
- Sem efeitos colaterais em tempo de import.

## 2. Nomenclatura declarativa

- Nomes **completos e descritivos**: `produto`, `pedido`, `download_grant`.
- **Proibido** abreviar/encurtar artificialmente: ❌ `prod_x`, `ped`, `dg` → ✅ `produto`, `pedido`, `download_grant`.
- Funções/métodos = **verbos** (`criar_pedido`, `validar_grant`); classes = **substantivos** (`OrderCreator`).
- Booleanos com prefixo de estado: `is_published`, `has_expired`, `can_download`.

## 3. Laços explícitos — sem comprehension/lambda

**Regra:** sempre usar laço `for` explícito. **Proibido** list/dict/set comprehension e `lambda`.

### ✅ Certo
```python
publicados = []
for produto in produtos:
    if produto.is_published:
        publicados.append(produto)
```

### ❌ Errado
```python
publicados = [produto for produto in produtos if produto.is_published]   # comprehension
ordenados = sorted(produtos, key=lambda produto: produto.preco)          # lambda
```
Para ordenação, usar função nomeada:
```python
def por_preco(produto):
    return produto.preco

ordenados = sorted(produtos, key=por_preco)
```

> 💡 **Por que isto não é 100% automático:** o Ruff não tem regra que *proíba*
> comprehensions (a regra `C4` faz o contrário). Por isso **não habilitamos `C4`**
> e esta regra é cobrada na **revisão de PR** (ver [`enforcement.md`](enforcement.md)).
> `lambda` em si é sinalizável, mas a política aqui é bani-lo por convenção.

## 4. Estrutura de código (regras estruturais — obrigatórias)

- **Sem `def` dentro de `def`** (sem funções aninhadas/closures). Para "fábricas" de
  comportamento (ex.: dependencies parametrizadas do FastAPI), use **classe chamável**
  (`__call__`), não closure.
- **Sem arquivo contendo apenas funções soltas.** Helpers viram **métodos de uma classe**
  coesa (ex.: `StatusMapper.to_order_status(...)` em vez de uma função `map_provider_status`).
- **Sem classe dentro de classe** no mesmo arquivo (sem classes aninhadas).
- Uma responsabilidade por classe (ver [`solid.md`](solid.md)); métodos curtos.

### Exceção mínima e explícita (FastAPI)
O FastAPI exige **funções** para *route handlers* e *dependencies*. É permitido que
esses pontos sejam **funções finas no `router.py`/`deps.py`**, desde que:
1. sejam só "cola" (validam entrada e **delegam a uma classe**, sem regra de negócio);
2. tenham **docstring** (pt-BR);
3. não contenham `def` aninhado (use classe chamável quando precisar parametrizar).

```python
class RequireRole:
    """Dependency chamável que autoriza por papel (RBAC)."""

    def __init__(self, *allowed: str) -> None:
        self.allowed = allowed

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        """Permite o acesso se o usuário tiver um papel permitido; senão 403."""
        ...
```

## 5. Outras convenções

- **Docstring em TODA funcionalidade** (ver [`docstrings-and-language.md`](docstrings-and-language.md)).
- Código em inglês; **comentários/docstrings em pt-BR**; arquivos UTF-8.
- O nome explica o **o quê**; a docstring explica o **porquê/contrato**.
