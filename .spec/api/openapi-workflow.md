# OpenAPI: geração, exportação e contract testing

> Trilha API · e_seller · 2026-06-06

---

## 1. Fonte da verdade

O **FastAPI gera o OpenAPI automaticamente** a partir dos routers e schemas Pydantic:
- `GET /openapi.json` — documento OpenAPI.
- `GET /docs` (Swagger) e `/redoc` — UIs.

## 2. Exportar o schema (versionado)

Gerar `openapi.json` em build/CI e versionar um snapshot (ex.: `backend/openapi.json`)
para revisão de diffs de contrato em PRs.

```
# pseudo-passo no CI
python -c "import json; from app.main import create_app; \
print(json.dumps(create_app().openapi()))" > openapi.json
```

## 3. Contract testing

- **Backend:** teste que verifica que endpoints/Schemas esperados existem no OpenAPI
  (pega remoção/renome acidental). Ver [`../unit/tests/io_testing.md`](../unit/tests/io_testing.md).
- **Frontend (separado):** pode gerar um client a partir do `openapi.json` — mudanças
  de contrato aparecem como diff/quebra de build.

## 4. Política

- Toda mudança de contrato atualiza [`endpoints.md`](endpoints.md)/[`errors.md`](errors.md) e o snapshot.
- Mudança incompatível → nova versão (`/api/v2`) — ver [`conventions.md`](conventions.md).
- CI falha se o snapshot divergir sem atualização (diff de `openapi.json`).

## 5. Pendências

- [ ] Onde versionar o snapshot (repo backend).
- [ ] Gerar client do frontend a partir do OpenAPI (quando a tech for escolhida).
