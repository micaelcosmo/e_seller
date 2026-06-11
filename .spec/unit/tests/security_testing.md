# Guia: Testes de Segurança

> Guia de testes · Área: `tests` · 2026-06-06
> Como testar os requisitos de segurança. Mapeia os RNF e as units de
> [`../security/`](../security/). Os trechos são exemplos ilustrativos.

---

## 1. Princípio

Segurança é **comportamento testável**: cada controle de segurança tem teste que
prova que ele bloqueia o caminho malicioso, não só que libera o caminho feliz.

## 2. Matriz de testes de segurança

| Controle | RNF/RF | Unit | Cenário-chave |
|---|---|---|---|
| Download só com pagamento confirmado | RNF-01 | `payments/service_process_webhook` | retorno do navegador **não** libera |
| Assinatura do webhook | RNF-02 | `security/webhook_signature` | assinatura inválida → rejeita |
| Idempotência do webhook | RNF-20 | `payments/service_process_webhook` | webhook repetido → sem efeito |
| Arquivo não público / path traversal | RNF-03 | `security/file_protection` | `../../etc/passwd` → bloqueado |
| Token de download (expira/limite) | RF-31 | `delivery/service_validate_grant` | expirado/limite → nega |
| Token seguro | RF-30 | `security/download_token` | imprevisível, único |
| Auth JWT | RF-50 | `security/jwt_tokens`, `auth_dependency` | sem/expirado/adulterado → 401 |
| Autorização (staff) | RF-50 | `security/auth_dependency` | não-staff → 403 |
| Hash de senha | ADR-007 | `security/password_hashing` | não guarda senha em claro |
| Segredos fora do repo | RNF-04 | `security/secrets_management` | scan não encontra segredo |
| LGPD: exclusão | RNF-06 | `security/lgpd_data_handling` | anonimiza e remove payload |

## 3. Exemplos

### RNF-01 — retorno do navegador não libera download
```python
def test_retorno_sem_webhook_nao_libera_download(client, db_session):
    pedido = OrderFactory(status=OrderStatus.PENDING)

    # cliente "volta" à página de sucesso, mas nenhum webhook foi processado
    resposta = client_get_status(client, pedido.reference)

    assert resposta.json()["status"] == "pending"
    assert not has_download_grant(db_session, pedido)
```

### RNF-02 — assinatura de webhook inválida
```python
async def test_webhook_assinatura_invalida_e_rejeitado(client):
    resposta = await client.post(
        "/api/webhooks/mercadopago",
        headers={"x-signature": "invalida"},
        json={"id": "123"},
    )
    assert resposta.status_code in (401, 403)
```

### RNF-20 — idempotência
```python
def test_webhook_duplicado_nao_cria_novo_grant(db_session):
    processor = WebhookProcessor(FakePaymentGateway(payment_status="approved"),
                                 db_session, issuer)
    n1 = processor.process(notification)   # APPLIED
    n2 = processor.process(notification)   # mesmo provider_payment_id

    assert n2.outcome == "ALREADY_PROCESSED"
    assert count_grants(db_session) == 1
```

### RNF-03 — path traversal
```python
def test_path_traversal_e_bloqueado(tmp_path):
    storage = ProtectedStorage(root=tmp_path)
    with pytest.raises(PathTraversalError):
        storage.resolve("../../etc/passwd")
```

### RF-50 — auth: sem token / expirado / sem permissão
```python
async def test_rota_admin_sem_token_retorna_401(client):
    resposta = await client.get("/api/admin/algo")
    assert resposta.status_code == 401


def test_jwt_expirado_e_recusado(frozen_clock):
    jwt = JwtService(secret_key="s", clock=frozen_clock, ttl_minutes=1)
    token = jwt.issue(subject="user@x")
    frozen_clock.advance(minutes=2)
    with pytest.raises(ExpiredToken):
        jwt.verify(token)
```

### RNF-04 — nenhum segredo no repositório
```python
def test_dotenv_esta_no_gitignore():
    assert ".env" in read_gitignore_patterns()
# Complemento no CI: scanner de segredos (ex.: gitleaks) — ver infra/ci_pipeline.
```

## 3b. Domínios da visão completa (Tiers 🟡/🔵)

| Controle | Unit | Cenário-chave |
|---|---|---|
| Autorização RBAC | `security/rbac_authorization` | papel insuficiente → `403`; admin → ok |
| Review só de comprador | `reviews/service_review` | não-comprador → `NotEntitled`/`403` |
| Cupom: fraude/abuso | `coupons/service_coupon` | expirado/esgotado → inválido; resgate duplo no pedido → idempotente |
| Posse única do e-book | `entitlement/model_entitlement` | recomprar/possuir 2x → bloqueado (UNIQUE) |
| Reemissão de download | `entitlement/router_library` | só item possuído; não possuído → `403` |
| Estorno revoga acesso | `payments/service_refund` | após `refunded`, download negado |
| Consentimento newsletter (LGPD) | `newsletter/service_newsletter` | double opt-in; opt-out respeitado |
| PII fiscal (CPF) | `billing/model_billing_profile` | minimização; sujeito à exclusão LGPD |
| Download log sem IP cru | `delivery/model_download_log` | IP armazenado em hash |

```python
def test_papel_insuficiente_retorna_403(client, db_session):
    user = UserFactory()  # sem papel admin
    resposta = get_with_auth(client, "/api/v1/coupons", user)  # rota só-admin
    assert resposta.status_code == 403
```

## 4. Boas práticas

- Sempre testar o **caminho negado** (401/403/410/expirado/limite), não só o feliz.
- Mensagens de erro **genéricas** (não revelar existência de recurso/usuário).
- Validar autenticidade na borda (dependency) e idempotência no service.
- Nunca logar segredos/tokens nos testes nem no código.

## 5. Relacionado

[`io_testing`](io_testing.md) · [`mocking_guide`](mocking_guide.md) ·
units de [`../security/`](../security/) · planning [`19`](../../planning/19-seguranca-e-lgpd.md), [`20`](../../planning/20-entrega-ebook-anti-pirataria.md)
