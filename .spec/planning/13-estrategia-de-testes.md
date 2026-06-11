# 13 — Estratégia de Testes (TDD)

> Documento de planning · e_seller · 2026-06-06
> Como praticamos Test-Driven Development no e_seller.

---

## 1. O ciclo TDD (Red → Green → Refactor)

```
1. RED      escreva um teste que descreve o comportamento desejado → ele FALHA
2. GREEN    escreva o MÍNIMO de código para o teste passar
3. REFACTOR melhore o código mantendo os testes verdes
```

> 💡 *Por que escrever o teste antes?* Garante que (a) há um requisito claro,
> (b) o código nasce testável, (c) você só escreve o necessário. O teste é a
> tradução executável da spec.

## 2. Pirâmide de testes

```
        ╱  E2E  ╲          poucos — fluxo completo (compra→pagamento→download)
      ╱──────────╲
    ╱ integração   ╲       médios — view + db + webhook (mockando Mercado Pago)
  ╱──────────────────╲
 ╱     unitários       ╲   muitos — services/regras de negócio, rápidos
```

- **Unitários:** regras puras (preço congelado, validade de grant, transições de estado).
- **Integração:** views + banco; webhook end-to-end com gateway **mockado**.
- **E2E (poucos):** o fluxo crítico do MVP, em ambiente Docker.

## 3. Ferramentas

| Ferramenta | Uso |
|---|---|
| **pytest** + **pytest-asyncio** | runner principal; suporte a testes `async`. |
| **httpx** (`ASGITransport`/`TestClient`) | chamar a API FastAPI em memória, sem subir servidor. |
| **coverage** (via `pytest-cov`) | medir cobertura das regras críticas. |
| **factory_boy** (ou fixtures) | criar dados de teste legíveis. |
| **respx**/**httpx mock** | simular a API do Mercado Pago. |
| **freezegun** | controlar o tempo (expiração de grants). |

> 💡 *Sem `pytest-django`:* no FastAPI, testamos a aplicação com o **httpx** apontando
> direto para o app ASGI (`ASGITransport`) — rápido e sem rede. Para o banco, usamos
> uma sessão SQLAlchemy de teste com transação revertida a cada teste.

Todas open-source (RNF-42).

## 4. O que SEMPRE tem teste (crítico)

Mapeado a partir de [`05-user-stories.md`](05-user-stories.md):

| Comportamento | Tipo | Story |
|---|---|---|
| Catálogo só mostra publicados | integração | US-01 |
| Validação de upload de arquivo | unit/integração | US-03 |
| Criação de pedido + checkout | integração | US-04 |
| Webhook aprova pedido | integração | US-05 |
| Webhook idempotente (duplicado) | integração | US-05 |
| Retorno do navegador NÃO libera download | integração | US-05 |
| Download válido / expirado / limite | integração | US-06 |
| Máquina de estados do pedido | unit | US-05 |

## 5. Convenções de teste

- Um cenário Gherkin → um teste nomeado de forma descritiva
  (`test_webhook_duplicado_nao_cria_novo_grant`).
- **Arrange / Act / Assert** explícito.
- Testes isolados (sem rede real, sem ordem dependente).
- Banco de teste efêmero; transações revertidas entre testes.
- Tempo determinístico (freeze) para expirações.

## 6. Metas de cobertura

- Foco em **cobrir regras de negócio críticas** (pagamento, entrega, estados).
- Cobertura não é meta cega; mas **CI falha** se cair abaixo do limite acordado
  (sugestão inicial: 85% nas apps de domínio). Detalhe em [`15-ci-cd.md`](15-ci-cd.md).

## 7. Definição de "teste bom" aqui

- Falha por um motivo claro.
- Não testa detalhes de implementação, e sim comportamento observável.
- Roda rápido (a maioria em milissegundos).

## 8. Pendências

- [ ] Confirmar limite de cobertura no CI.
- [ ] factory_boy vs fixtures simples (decidir na implementação).
