# 11 — Contratos da API

> Documento de planning · e_seller · 2026-06-06 (revisado p/ FastAPI, API JSON)
> Como o backend e o frontend estão **separados**, o backend é uma **API JSON pura**.
> Estes são os contratos que qualquer frontend (ou o Mercado Pago) consome.

---

## 1. Convenções

- Prefixo **`/api`** para a API; **`/docs`** expõe o **OpenAPI/Swagger automático** do FastAPI.
- Recursos públicos usam `slug`/`reference` (nunca o `id` sequencial).
- Entradas e saídas validadas por **schemas Pydantic**.
- Erros padronizados: `{ "detail": "<mensagem>" }` com código HTTP adequado.
- **CORS** habilitado para o domínio do frontend.

> 💡 *Vantagem do FastAPI:* o contrato abaixo vira **documentação interativa** em
> `/docs` automaticamente, a partir dos schemas Pydantic. O frontend pode até gerar
> um client a partir do OpenAPI.

## 2. Catálogo (público)

| Método | Rota | Descrição | RF |
|---|---|---|---|
| GET | `/api/products` | Lista e-books publicados (paginado) | RF-01 |
| GET | `/api/products/{slug}` | Detalhe do e-book | RF-02 |
| GET | `/api/products?q=` | Busca por título/autor | RF-03 |
| GET | `/api/categories` | Lista categorias | RF-13 |

### Schema de saída — `ProductOut`
```json
{
  "slug": "python-na-pratica",
  "title": "Python na Prática",
  "author": "Fulano",
  "description": "…",
  "price": "39.90",
  "cover_url": "https://.../cover.jpg",
  "category": "Programação"
}
```
> O arquivo do e-book **nunca** aparece no catálogo (só após compra/entrega).

## 3. Compra & pedido (público)

| Método | Rota | Descrição | RF |
|---|---|---|---|
| POST | `/api/orders` | Cria pedido `pending` + checkout | RF-20,21,22 |
| GET | `/api/orders/{reference}` | Status do pedido (acompanhamento) | RF-25 |

### Contrato — `POST /api/orders`
**Entrada (`OrderCreateIn`)**
```json
{ "product_slug": "python-na-pratica", "buyer_email": "leitor@exemplo.com" }
```
**Saída 201 (`OrderOut`)**
```json
{
  "reference": "0c5a…uuid",
  "status": "pending",
  "amount": "39.90",
  "checkout_url": "https://www.mercadopago.com/checkout/..."
}
```
**Erros:** 422 (validação Pydantic, ex.: e-mail inválido), 404 (produto não publicado).

## 4. Webhook de pagamento (Mercado Pago)

| Método | Rota | Descrição | RF/RNF |
|---|---|---|---|
| POST | `/api/webhooks/mercadopago` | Notificação de pagamento | RF-23,24 / RNF-01,02,20 |

### Contrato
- **Autenticação:** validar assinatura/segredo do Mercado Pago (RNF-02).
- **Processamento:**
  1. Buscar o pagamento na API do Mercado Pago pelo id (não confiar só no corpo).
  2. Mapear status → estado do pedido.
  3. **Idempotência:** se `provider_payment_id` já processado → `200` sem reefeito.
  4. Se aprovado e pedido `pending` → `paid` + emitir `DownloadGrant`.
- **Resposta:** `200 OK` rápido (RNF-11). Erro transitório → status que faça o
  Mercado Pago **reenviar** depois.

```gherkin
# Contrato comportamental (ver US-05)
Dado um webhook válido de pagamento aprovado para um pedido pendente
Quando processado
Então o pedido fica "pago" e um grant é criado
E reprocessar o mesmo webhook não cria novo grant
```

## 5. Entrega (download)

| Método | Rota | Descrição | RF/RNF |
|---|---|---|---|
| GET | `/api/download/{token}` | Baixa o arquivo se o grant for válido | RF-30,31,33 / RNF-03 |

### Contrato
- Valida: grant existe, **não expirado**, `download_count < max_downloads`.
- Sucesso: incrementa `download_count` e faz **streaming** do arquivo
  (`StreamingResponse`/`FileResponse`), **sem** revelar o caminho físico.
- Erros: 404/410 (token inválido/expirado), 403/429 (limite atingido).

## 6. Autenticação de admin

| Método | Rota | Descrição | RF |
|---|---|---|---|
| POST | `/api/auth/token` | Login do admin (OAuth2 password) → JWT | RF-50 |

- Demais rotas administrativas exigem `Authorization: Bearer <jwt>` (ADR-007).

## 7. Administração (P2)

No MVP, a administração usa o painel **SQLAdmin** montado no backend (rota tipo
`/admin`), cobrindo:
- CRUD de `Product`/`Category` (RF-10..13)
- Listagem/detalhe de `Order` e `Payment` (RF-40,41)

> 💡 *Por que SQLAdmin?* O FastAPI não tem admin embutido (diferente do Django).
> O SQLAdmin entrega um painel CRUD gratuito sobre os models SQLAlchemy, sem
> precisar do frontend dedicado ainda (ADR-008).

## 8. Documentação do contrato

- **OpenAPI** gerado automaticamente em `/openapi.json`; UI em `/docs` (Swagger) e `/redoc`.
- Serve de contrato estável para o **frontend separado** (ADR-005).

## 9. Pendências

- [ ] Paginação: formato (limit/offset vs cursor).
- [ ] Formato exato do payload do Mercado Pago (confirmar na doc/sandbox).
- [ ] Versionamento da API (`/api/v1`?) — provavelmente sim desde o início.
- [ ] Política de CORS (domínios permitidos por ambiente).
