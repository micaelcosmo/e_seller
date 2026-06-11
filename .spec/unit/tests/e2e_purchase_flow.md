# Unit: e2e_purchase_flow (`tests`/E2E)

> Tipo: `tests` (E2E) · Área: `tests`
> Deriva de: [`planning/06`](../../planning/06-escopo-mvp.md) §4, [`13`](../../planning/13-estrategia-de-testes.md) ·
> US-01..06 · Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Teste de ponta a ponta do fluxo crítico do MVP: publicar → comprar → pagar (webhook) → baixar.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/tests/e2e/test_purchase_flow.py` |

## 3. Contrato (roteiro)

```gherkin
Dado um produto publicado
Quando o cliente cria um pedido (POST /api/orders)
E o webhook de pagamento aprovado é processado
Então o pedido fica "paid" e um download_grant é criado
E o cliente baixa o arquivo (GET /api/download/{token})
E um segundo webhook idêntico não duplica nada
E o download respeita expiração e limite
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `conftest_client` | client httpx |
| `mercadopago_mock` | gateway fake |
| `time_control` | expiração |
| fluxo completo backend | sob teste |

## 5. Comportamento / regras

- Usa fakes (sem rede); banco de teste real.
- Cobre os cenários "Must" de [`05-user-stories`](../../planning/05-user-stories.md).
- Valida idempotência e RNF-01 (retorno do navegador não libera download).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Fluxo feliz completo | pedido `paid`, download OK |
| T2 | Webhook duplicado | sem efeito extra |
| T3 | Retorno sem webhook | download negado |
| T4 | Link expirado/limite | download negado |

## 7. Rastreabilidade

- US-01..06 · Planning [`06`](../../planning/06-escopo-mvp.md) §4 · Units: todos os routers/services do fluxo

## 8. Pendências

- [ ] Marcar como `e2e` (execução separada/possivelmente mais lenta).
