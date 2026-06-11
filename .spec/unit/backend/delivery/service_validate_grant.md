# Unit: GrantValidator (`service`)

> Tipo: `service` · Área: `backend/delivery`
> Deriva de: US-06 · RF-31 · RNF-01 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Validar um token de download: existência, expiração e limite; e incrementar o contador.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/delivery/services.py::GrantValidator` |
| Teste | `backend/tests/delivery/test_validate_grant.py` |

## 3. Contrato

```python
class GrantValidator:
    def __init__(self, session: Session, clock: Clock) -> None:
        self.session = session
        self.clock = clock

    def consume(self, token: str) -> DownloadGrant:
        ...  # levanta GrantNotFound | GrantExpired | DownloadLimitReached
```

- **Saída:** grant válido (com `download_count` incrementado).
- **Erros:** `GrantNotFound` (404/410), `GrantExpired` (410), `DownloadLimitReached` (403/429).

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `session` / `model_download_grant` | consulta/atualização | real |
| `clock` (tempo) | comparar expiração | **injetado/freezegun** |

## 5. Comportamento / regras

- Inválido se token não existe, `now >= expires_at`, ou `download_count >= max_downloads`.
- Em sucesso, **incrementa `download_count`** de forma atômica (evitar corrida).
- Nunca libera por "retorno" do navegador — só por grant válido (RNF-01).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Token válido | retorna grant; count +1 |
| T2 | Token inexistente | `GrantNotFound` |
| T3 | Expirado | `GrantExpired` |
| T4 | Limite atingido | `DownloadLimitReached` |
| T5 | Concorrência no limite | não ultrapassa `max_downloads` |

## 7. Rastreabilidade

- RF-31 · RNF-01 · US-06 · Units: `model_download_grant`, `service_stream_file`, `router_download`, `tests/time_control`

## 8. Pendências

- [ ] Incremento via UPDATE atômico (lock otimista) vs `SELECT ... FOR UPDATE`.
