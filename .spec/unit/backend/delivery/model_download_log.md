# Unit: DownloadLog (`model`)

> Tipo: `model` · Área: `backend/delivery` · Tier 🟡
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md), [`planning/20`](../../../planning/20-entrega-ebook-anti-pirataria.md) ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Auditoria de cada download efetivo (anti-pirataria e suporte).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/delivery/models.py::DownloadLog` |
| Teste | `backend/tests/delivery/test_model_download_log.py` |

## 3. Contrato

```python
class DownloadLog(Base):
    __tablename__ = "download_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    download_grant_id: Mapped[int] = mapped_column(ForeignKey("download_grant.id"))
    downloaded_at: Mapped[datetime]
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)   # hash, não IP cru (LGPD)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
```

## 4. Comportamento / regras

- Registrado a cada download bem-sucedido (no `GrantValidator`/`router_download`).
- **IP em hash**, não em claro (minimização LGPD).
- Retenção sujeita à política LGPD ([`../../security/lgpd_data_handling.md`](../../security/lgpd_data_handling.md)).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Download bem-sucedido | gera 1 log |
| T2 | IP é armazenado em hash | não há IP cru |

## 6. Rastreabilidade

- RNF-05 · Units: `service_validate_grant`, `router_download`, `observability/logging`

## 7. Pendências

- [ ] Política de retenção do log.
