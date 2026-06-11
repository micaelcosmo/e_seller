# Catálogo de Erros da API

> Trilha API · e_seller · 2026-06-06

---

## Códigos por situação

| HTTP | Quando | Exemplo |
|---|---|---|
| 200 | sucesso (leitura/operação) | listar produtos |
| 201 | recurso criado | criar pedido |
| 400 | requisição malformada | corpo inválido (não-Pydantic) |
| 401 | não autenticado | rota protegida sem/ com JWT inválido |
| 403 | sem permissão | não-staff em rota admin |
| 404 | recurso inexistente | produto/pedido não encontrado |
| 410 | recurso expirado | link de download expirado |
| 422 | validação | e-mail inválido (Pydantic) |
| 429 | limite excedido | downloads acima do limite |
| 500 | erro interno | falha inesperada (logada) |

## Regras

- Corpo de erro: `{ "detail": "..." }`.
- Mensagens **genéricas** para não vazar existência de recursos/usuários (segurança).
- `422` traz detalhamento por campo (padrão FastAPI/Pydantic).
- Webhook: erro **transitório** retorna status que faz o Mercado Pago **reenviar**;
  erro **permanente** (ex.: assinatura inválida) → `401/403` sem reenvio útil.

## Mapeamento exceção → HTTP (referência)

| Exceção (domínio) | HTTP |
|---|---|
| `ProductNotFound`, `OrderNotFound`, `GrantNotFound` | 404 |
| `GrantExpired` | 410 |
| `DownloadLimitReached` | 403/429 |
| `InvalidCredentials` | 401 |
| `InvalidSignature` | 401/403 |
| `InvalidTransition` | 409/422 |
