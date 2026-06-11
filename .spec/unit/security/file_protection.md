# Unit: ProtectedStorage (`security`)

> Tipo: `security` · Área: `security`
> Deriva de: RNF-03 · RF-33 · [`planning/20`](../../planning/20-entrega-ebook-anti-pirataria.md) ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Garantir que arquivos de e-book vivam em local **não servido publicamente** e que o
acesso seja sempre resolvido com segurança (sem path traversal).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/security/storage.py::ProtectedStorage` |
| Teste | `backend/tests/security/test_file_protection.py` |

## 3. Contrato

```python
class ProtectedStorage:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def resolve(self, relative_name: str) -> Path:
        ...  # garante que o caminho final está DENTRO de root; senão PathTraversalError

    def save(self, relative_name: str, data: BinaryIO) -> None: ...
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| volume protegido (`ebook_files`) | armazenamento ([`infra/volumes`](../infra/README.md)) |

## 5. Comportamento / regras

- `resolve` normaliza e verifica que o caminho final fica dentro de `root` (anti path traversal).
- Nada deste volume é exposto por rota estática (RNF-03).
- Único acesso é via `delivery/FileStreamer` após grant válido.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Nome simples | resolve dentro de root |
| T2 | `../../etc/passwd` | `PathTraversalError` |
| T3 | Arquivo público? | não há rota estática para o volume |

## 7. Rastreabilidade

- RNF-03 · RF-33 · Units: `delivery/service_stream_file`, `admin/admin_views_product`, `infra/volumes`

## 8. Pendências

- [ ] Migrar para storage de objeto (S3-compatível) no futuro.
