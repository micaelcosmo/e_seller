# Unit: volumes (`infra`)

> Tipo: `infra` · Área: `infra`
> Deriva de: [`planning/12`](../../planning/12-docker-e-ambientes.md) · RNF-03 ·
> Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Definir os volumes Docker e a separação entre arquivos **protegidos** e públicos.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `docker-compose.yml` (seção volumes) |
| Teste | verificação manual/smoke |

## 3. Volumes (contrato)

| Volume | Conteúdo | Acesso |
|---|---|---|
| `pgdata` | Dados do PostgreSQL | interno |
| `ebook_files` | Arquivos de e-book | **protegido** (nunca rota estática) |
| `media` | Capas/estáticos públicos | público |

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `security/file_protection` | resolve caminhos do `ebook_files` |
| `docker_compose` | montagem |

## 5. Comportamento / regras

- `ebook_files` **não** é servido por servidor estático (RNF-03); só via `delivery`.
- `media` pode ser servido (capas).
- Permissões compatíveis com o usuário não-root do container.

## 6. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | Persistência do db | dados sobrevivem a restart |
| T2 | `ebook_files` não público | sem URL estática que o exponha |

## 7. Rastreabilidade

- RNF-03 · Units: `security/file_protection`, `delivery/service_stream_file`

## 8. Pendências

- [ ] Migrar `ebook_files` para storage de objeto no futuro.
