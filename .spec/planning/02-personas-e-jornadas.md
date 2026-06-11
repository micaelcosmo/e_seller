# 02 — Personas e Jornadas

> Documento de planning · e_seller · 2026-06-06
> Quem usa o produto e como percorre os fluxos principais.

---

## 1. Personas

### P1 — Leitor/Comprador (Cliente)
- **Quer:** achar um e-book, pagar fácil (Pix) e baixar na hora.
- **Dores:** checkout confuso, medo de pagar e não receber, link de download que expira sem aviso.
- **Conhecimento técnico:** baixo.

### P2 — Administrador/Vendedor (Operador)
- **Quer:** cadastrar e-books (título, capa, preço, arquivo), acompanhar vendas e ver o que foi entregue.
- **Dores:** subir arquivo grande, controlar estoque digital, identificar pagamentos.
- **Conhecimento técnico:** médio. Usa um **painel administrativo** no MVP.

> 💡 *E o admin no FastAPI?* Diferente do Django, o FastAPI **não** traz um admin
> pronto. Para o MVP, a proposta é usar **SQLAdmin** (biblioteca gratuita de painel
> administrativo para SQLAlchemy) — entrega CRUD e login com pouco esforço, sem
> esperar o frontend dedicado. Decisão registrada em [`07-adr-stack.md`](07-adr-stack.md) (ADR-004/008).

### P3 — Sistema externo (Mercado Pago)
- **Não é gente**, mas é um "ator": envia **webhooks** de confirmação de pagamento.
- **Quer (do nosso lado):** um endpoint confiável que responda rápido e seja idempotente.

## 2. Jornada principal — Compra de e-book (P1)

```
Navega catálogo → Vê detalhe do e-book → Adiciona/Compra
   → Informa e-mail → Checkout (Mercado Pago) → Paga (Pix/cartão)
   → Mercado Pago confirma (webhook) → Pedido vira "pago"
   → Sistema gera link de download seguro → Leitor baixa o arquivo
```

Pontos críticos:
- O download **só** é liberado após confirmação real do pagamento (webhook), nunca
  só pelo "retorno" do navegador (que pode ser forjado).
- O link de download é **único, expira e é limitado** (ver [`20-entrega-ebook-anti-pirataria.md`](20-entrega-ebook-anti-pirataria.md)).

## 3. Jornada secundária — Publicar e-book (P2)

```
Login no Admin → Novo Produto → Preenche metadados + upload do arquivo + capa
   → Define preço e status (rascunho/publicado) → Publica
   → Produto aparece no catálogo
```

## 4. Jornada de exceção — Pagamento não confirmado

```
Checkout iniciado → Pagamento pendente/recusado
   → Pedido permanece "pendente"/"falho" → Download NÃO liberado
   → Leitor pode reabrir o pedido e tentar pagar de novo
```

## 5. Mapa persona × necessidade (entrada para requisitos)

| Necessidade | P1 Leitor | P2 Admin |
|---|---|---|
| Buscar/navegar catálogo | ✅ | ✅ |
| Detalhe do produto | ✅ | ✅ |
| Checkout + pagamento | ✅ | — |
| Receber/baixar e-book | ✅ | — |
| CRUD de produtos | — | ✅ |
| Ver pedidos/vendas | — | ✅ |

> Estas necessidades viram **RF** em [`03-requisitos-funcionais.md`](03-requisitos-funcionais.md).
