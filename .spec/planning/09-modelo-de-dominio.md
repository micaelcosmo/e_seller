# 09 — Modelo de Domínio

> Documento de planning · e_seller · 2026-06-06
> Entidades do negócio, seus relacionamentos e regras (invariantes).

---

## 1. Entidades principais

### Product (E-book)
Representa um e-book à venda.
- `title`, `author`, `slug`, `description`
- `price` (decimal, em BRL)
- `cover` (imagem da capa)
- `file` (arquivo do e-book — protegido)
- `status`: `draft` | `published`
- `category` (opcional)
- timestamps

**Invariantes**
- Preço ≥ 0.
- Só produtos `published` aparecem no catálogo.
- Arquivo obrigatório para publicar.

### Category
- `name`, `slug`. (Opcional no MVP.)

### Order (Pedido)
Uma intenção de compra de um produto.
- `reference` (UUID público — usado em URLs, não expõe id sequencial)
- `buyer_email`
- `product` (FK) e `unit_price` (preço "congelado" no momento da compra)
- `amount` (total)
- `status`: `pending` | `paid` | `failed` | `cancelled` | `refunded`
- timestamps

**Invariantes**
- `amount` é fixado na criação (não muda se o preço do produto mudar depois).
- Transições de status seguem a máquina de estados (abaixo).
- Só pedido `paid` pode originar entrega.

> 💡 *Por que "congelar" o preço?* Se o admin mudar o preço amanhã, o pedido de hoje
> não pode mudar de valor. Guardar `unit_price`/`amount` no pedido garante histórico correto.

### Payment (Pagamento)
Registro do pagamento associado a um pedido (espelha o Mercado Pago).
- `order` (FK)
- `provider` = `mercadopago`
- `provider_payment_id` (id no Mercado Pago)
- `status` (mapeado do provedor)
- `raw_payload` (auditoria)
- `processed_at`

**Invariantes**
- `provider_payment_id` único → base da **idempotência** do webhook.

### DownloadGrant (Concessão de download)
Autorização de download emitida após pagamento.
- `order` (FK)
- `token` (aleatório, único, secreto)
- `expires_at`
- `max_downloads`, `download_count`
- timestamps

**Invariantes**
- Download válido apenas se: não expirado **e** `download_count < max_downloads`.
- Token nunca reutilizado entre pedidos.

## 2. Relacionamentos

```
Category 1───* Product
Product  1───* Order
Order    1───1 Payment        (no MVP: um pagamento efetivo por pedido)
Order    1───* DownloadGrant  (normalmente 1; * permite reemissão)
```

## 3. Máquina de estados do Pedido (Order)

```
            criar
              │
              ▼
          ┌────────┐   webhook aprovado    ┌──────┐
          │pending │ ─────────────────────►│ paid │
          └───┬────┘                        └──┬───┘
              │ webhook recusado/expirado      │ estorno
              ▼                                 ▼
          ┌────────┐                        ┌──────────┐
          │ failed │                        │ refunded │
          └────────┘                        └──────────┘
              │ cancelar manual
              ▼
          ┌───────────┐
          │ cancelled │
          └───────────┘
```

Regras:
- `pending → paid`: **somente** via webhook válido (RNF-01).
- `paid` é o único estado que dispara `DownloadGrant`.
- Reprocessar webhook de um pedido já `paid` **não faz nada** (idempotência, RNF-20).
- Transições inválidas (ex.: `failed → paid` sem novo pagamento) são proibidas.

## 4. Regras de negócio-chave (resumo)

| Regra | Onde mora |
|---|---|
| Preço congelado no pedido | `orders` (criação) |
| Idempotência por `provider_payment_id` | `payments` (webhook) |
| Liberação de download só se `paid` | `orders` + `delivery` |
| Validade do download (expiração/limite) | `delivery` |

> Estas entidades viram tabelas em [`10-modelo-de-dados.md`](10-modelo-de-dados.md).
