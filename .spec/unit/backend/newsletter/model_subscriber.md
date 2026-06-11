# Unit: NewsletterSubscriber (`model`)

> Tipo: `model` · Área: `backend/newsletter` · Tier 🔵
> Deriva de: [`db/schema_overview`](../../db/schema_overview.md) · LGPD ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Inscrição em newsletter (e-mail), com consentimento e opt-out.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/newsletter/models.py::NewsletterSubscriber` |
| Teste | `backend/tests/newsletter/test_model_subscriber.py` |

## 3. Contrato

```python
class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscriber"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    confirmed: Mapped[bool] = mapped_column(default=False)   # double opt-in
    unsubscribed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime]
```

## 4. Comportamento / regras

- `email` único.
- **Consentimento (LGPD):** double opt-in (`confirmed`); opt-out (`unsubscribed_at`).
- Dado pessoal → sujeito à exclusão LGPD ([`../../security/lgpd_data_handling.md`](../../security/lgpd_data_handling.md)).

## 5. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Inscrever | criado `confirmed=False` |
| T2 | E-mail duplicado | viola UNIQUE |

## 6. Rastreabilidade

- RNF-05,06 · Units: `service_newsletter`

## 7. Pendências

- [ ] Fluxo de confirmação por e-mail.
