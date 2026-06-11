# 01 — Visão de Produto

> Documento de planning · e_seller · 2026-06-06
> Define **por que** o produto existe. Tudo a seguir deriva daqui.

---

## 1. Resumo (elevator pitch)

O **e_seller** é um portal onde autores e pequenas editoras vendem **e-books**
diretamente ao leitor, com pagamento via **Mercado Pago** e **entrega digital
imediata e segura** após a confirmação do pagamento.

## 2. Problema

- Autores independentes têm dificuldade de vender e-books sem depender de grandes
  marketplaces (que cobram comissões altas e escondem o cliente final).
- Leitores querem comprar de forma simples, pagar com Pix/cartão e baixar na hora.
- Soluções caseiras geralmente falham em: **segurança da entrega** (link vaza),
  **confirmação de pagamento** e **controle de catálogo**.

## 3. Proposta de valor

| Para | O e_seller oferece | Diferente de |
|---|---|---|
| Leitor | Compra rápida, pagamento BR (Pix/cartão/boleto) e download imediato | Lojas lentas / sem Pix |
| Vendedor/Admin | Catálogo próprio, controle de vendas e entrega protegida | Marketplaces com comissão alta |

## 4. Objetivos do produto

1. Permitir **publicar e vender** e-books com catálogo navegável.
2. Processar pagamentos de forma confiável via Mercado Pago.
3. Garantir **entrega digital segura** (somente quem pagou baixa).
4. Operar com **custo inicial zero** de infraestrutura (open-source + Docker local).

## 5. Não-objetivos (por enquanto)

- Não seremos um marketplace multi-vendedor com repasses automáticos (fica para depois).
- Não faremos leitura online (reader embutido) no MVP.
- Não trataremos produtos físicos.

## 6. Métricas de sucesso (KPIs)

> 💡 *Por que definir métricas agora?* Elas guiam o que vale a pena construir.
> Sem meta, todo recurso "parece" importante.

- **Conversão:** % de visitantes que concluem uma compra.
- **Taxa de entrega bem-sucedida:** downloads válidos / pagamentos aprovados (meta: ~100%).
- **Tempo até o download:** do pagamento aprovado ao primeiro download (meta: < 1 min).
- **Falhas de pagamento:** % de checkouts iniciados que falham por erro técnico (meta: < 1%).

## 7. Restrições conhecidas

- Stack fixada: **FastAPI + Python 3.14.5+**, **Docker** em todos os serviços.
- **Backend e frontend separados** (serviços/containers independentes, comunicação via API JSON).
- Banco: **PostgreSQL**.
- Pagamentos: **Mercado Pago**.
- Frontend: **a decidir** (não bloqueia o backend, que é API-first por natureza).
- **Custo inicial zero**: priorizar ferramentas gratuitas/open-source.

## 8. Perguntas em aberto

- [ ] É um único vendedor (a própria operação) ou múltiplos autores cadastram produtos?
- [ ] Haverá cupons/descontos no MVP?
- [ ] Precisamos emitir nota fiscal no MVP?

> Estas perguntas afetam personas e escopo — ver [`02-personas-e-jornadas.md`](02-personas-e-jornadas.md)
> e [`06-escopo-mvp.md`](06-escopo-mvp.md).
