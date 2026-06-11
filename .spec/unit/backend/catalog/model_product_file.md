# Unit: ProductFile (`model`)

> Tipo: `model` · Área: `backend/catalog` · Tier 🟡
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md), [`planning/20`](../../../planning/20-entrega-ebook-anti-pirataria.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Arquivos do e-book por **formato** (PDF/EPUB) e **versão** — substitui o `product.file` único.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/models.py::ProductFile` |
| Teste | `backend/tests/catalog/test_model_product_file.py` |

## 3. Contrato

```python
class ProductFile(Base):
    __tablename__ = "product_file"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    format: Mapped[str] = mapped_column(String(16))     # pdf|epub
    storage_path: Mapped[str] = mapped_column(String(500))  # volume protegido
    version: Mapped[int] = mapped_column(default=1)
    size_bytes: Mapped[int] = mapped_column(default=0)
```

## 4. Comportamento / regras

- Caminho aponta para volume protegido (RNF-03); nunca público.
- Ponto natural para **watermark por comprador** na entrega ([`delivery/service_stream_file`](../delivery/service_stream_file.md)).
- A entrega escolhe o `ProductFile` pelo formato pedido.

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Produto com PDF e EPUB | dois arquivos |
| T2 | Nova versão | `version` incrementa |

## 6. Rastreabilidade

- RF-12,33 · RNF-03 · Units: `delivery/service_stream_file`, `security/file_protection`

## 7. Pendências

- [ ] Watermark por comprador (gera arquivo derivado na entrega).
