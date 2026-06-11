# .spec/api/

Trilha **viva** do contrato da API JSON do e_seller. Como **backend e frontend são
serviços separados** (ADR-005), este contrato é a **fonte da verdade** da integração.

> Fonte canônica em runtime: o **OpenAPI gerado pelo FastAPI** (`/openapi.json`, UI em
> `/docs`). Esta trilha documenta convenções, catálogo e regras que o código deve honrar.

## Documentos

| Doc | Assunto |
|---|---|
| [`conventions.md`](conventions.md) | Versionamento, formato de erro, paginação, auth, CORS. |
| [`endpoints.md`](endpoints.md) | Catálogo de endpoints (contrato consolidado). |
| [`errors.md`](errors.md) | Catálogo de erros e códigos HTTP. |
| [`openapi-workflow.md`](openapi-workflow.md) | Como exportar/validar o OpenAPI e testar contrato. |

## Regra de manutenção

Atualizar esta trilha **a cada mudança de contrato** (novo endpoint, novo campo,
mudança de erro/status) e registrar em [`CHANGELOG.md`](CHANGELOG.md). Specs e
OpenAPI nunca devem divergir (validar no CI — ver [`openapi-workflow.md`](openapi-workflow.md)).

## Relacionado

Planning [`11-contratos-api`](../planning/11-contratos-api.md) · units `backend/**/router_*`.
