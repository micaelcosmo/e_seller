# Unit: FileStreamer (`service`)

> Tipo: `service` · Área: `backend/delivery`
> Deriva de: US-06 · RF-33 · RNF-03 · [`planning/20`](../../../planning/20-entrega-ebook-anti-pirataria.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Transmitir o arquivo do e-book a partir do volume protegido, **sem** expor o caminho físico.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/delivery/services.py::FileStreamer` |
| Teste | `backend/tests/delivery/test_stream_file.py` |

## 3. Contrato

```python
class FileStreamer:
    def __init__(self, storage_root: Path) -> None:
        self.storage_root = storage_root

    def open_stream(self, product: Product) -> StreamInfo:
        ...  # resolve o path protegido; levanta FileMissing se ausente
```

- **Saída:** `StreamInfo` (iterador de bytes + nome/mimetype) para `StreamingResponse`.
- **Erros:** `FileMissing`.

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `storage_root` (volume protegido) | localizar arquivo | tmp dir de teste |
| `catalog/model_product` (`file`) | nome do arquivo | real |

## 5. Comportamento / regras

- Resolve o caminho **dentro** de `storage_root`; impede *path traversal*.
- Nunca devolve o caminho físico ao cliente (RNF-03).
- Stream em blocos (não carregar tudo em memória).
- O arquivo vive em volume não servido estaticamente ([`infra/volumes`](../../infra/README.md)).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Arquivo existe | retorna stream + nome/mimetype |
| T2 | Arquivo ausente | `FileMissing` |
| T3 | Tentativa de path traversal | bloqueado (erro) |

## 7. Rastreabilidade

- RF-33 · RNF-03 · US-06 · Units: `router_download`, `security/file_protection`

## 8. Pendências

- [ ] Watermark por comprador (Tier 🟡) — ponto de injeção aqui.
