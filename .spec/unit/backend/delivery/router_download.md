# Unit: router_download (`router`)

> Tipo: `router` · Área: `backend/delivery`
> Deriva de: [`planning/11`](../../../planning/11-contratos-api.md) §5 · RF-30,31,33 · RNF-03 ·
> Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Expor `GET /api/download/{token}`: valida o grant e transmite o arquivo.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/delivery/router.py` |
| Teste | `backend/tests/delivery/test_router_download.py` |

## 3. Contrato

```python
router = APIRouter(prefix="/api/download", tags=["delivery"])


@router.get("/{token}")
def download(token: str,
             validator: GrantValidator = Depends(get_grant_validator),
             streamer: FileStreamer = Depends(get_file_streamer)) -> StreamingResponse:
    grant = validator.consume(token)
    info = streamer.open_stream(grant.order_item.product)
    return StreamingResponse(info.chunks, media_type=info.mimetype, headers=...)
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `service_validate_grant` | validar/consumir token |
| `service_stream_file` | transmitir arquivo |

## 5. Comportamento / regras

- `404/410` para token inválido/expirado; `403/429` para limite (RF-31).
- Sucesso → `200` com streaming; sem expor path (RNF-03).
- Sem regra de negócio no router.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Token válido | `200` com o arquivo; count +1 |
| T2 | Token expirado | `410` |
| T3 | Limite atingido | `403/429` |
| T4 | Token inexistente | `404` |

## 7. Rastreabilidade

- RF-30,31,33 · RNF-03 · US-06 · Units: `service_validate_grant`, `service_stream_file`

## 8. Pendências

- [ ] Cabeçalhos `Content-Disposition` (nome do arquivo ao baixar).
