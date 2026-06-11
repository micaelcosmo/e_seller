# Unit: DownloadIssuer (`service`)

> Tipo: `service` · Área: `backend/delivery`
> Deriva de: US-05,06 · RF-30 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Emitir um `DownloadGrant` quando um item de pedido é pago (e registrar o `entitlement`).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/delivery/services.py::DownloadIssuer` |
| Teste | `backend/tests/delivery/test_issue_download.py` |

## 3. Contrato

```python
class DownloadIssuer:
    def __init__(self, session: Session, token_factory: TokenFactory,
                 max_downloads: int = 5, ttl_days: int = 7) -> None:
        self.session = session
        self.token_factory = token_factory
        self.max_downloads = max_downloads
        self.ttl_days = ttl_days

    def issue_for(self, order_item: OrderItem) -> DownloadGrant:
        ...
```

- **Saída:** `DownloadGrant` persistido.

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `session` | persistência | real |
| `security/download_token` (`TokenFactory`) | gerar token seguro | **fake/determinístico** |
| `model_download_grant` | entidade | real |

## 5. Comportamento / regras

- Só é chamado para item de pedido **pago** (garantido pelo `WebhookProcessor`).
- Calcula `expires_at = now + ttl_days`.
- Gera token via `token_factory` (injetado; testável).
- (Tier 🟡) cria/garante `entitlement` do usuário, se houver conta.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Item pago | cria grant com token, `expires_at` futuro, count 0 |
| T2 | TTL aplicado | `expires_at == now + ttl_days` (tempo controlado) |
| T3 | Reemissão | gera novo token, novo grant |

## 7. Rastreabilidade

- RF-30 · US-05,06 · Units: `model_download_grant`, `security/download_token`, `payments/service_process_webhook`

## 8. Pendências

- [ ] Vincular `entitlement` aqui ou em service próprio.
