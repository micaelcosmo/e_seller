# Unit: DownloadGrant (`model`)

> Tipo: `model` · Área: `backend/delivery`
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md), [`planning/20`](../../../planning/20-entrega-ebook-anti-pirataria.md) ·
> RF-30,31 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Mapear `download_grant` (link temporário de download). Distinto de `entitlement` (posse).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/delivery/models.py::DownloadGrant` |
| Teste | `backend/tests/delivery/test_model_download_grant.py` |

## 3. Contrato

```python
class DownloadGrant(Base):
    __tablename__ = "download_grant"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_item.id"))
    token: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime]
    max_downloads: Mapped[int] = mapped_column(default=5)
    download_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime]
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `core/db_session` (Base) | mapeamento |
| `orders/model_order` (OrderItem) | FK |

## 5. Comportamento / regras

- `token` único e **secreto** (gerado em [`security/download_token`](../../security/README.md)).
- Válido se `now < expires_at` **e** `download_count < max_downloads`.
- Reemissão cria novo grant (novo token), preserva histórico.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Criar grant | persiste; `download_count=0` |
| T2 | Token duplicado | viola UNIQUE |

## 7. Rastreabilidade

- RF-30,31 · Units: `service_issue_download`, `service_validate_grant`, `security/download_token`

## 8. Pendências

- [ ] Defaults: `max_downloads=5`, `ttl=7d` (confirmar).
