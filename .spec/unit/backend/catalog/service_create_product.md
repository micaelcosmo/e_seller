# Unit: ProductRegistrar (`service`) — cadastro dinâmico de e-book

> Tipo: `service` · Área: `backend/catalog` · Tier 🟡 (novo requisito 2026-06-07)
> Deriva de: pedido do Micael (cadastro dinâmico) · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Cadastrar um novo **e-book** (o produto é **sempre** e-book) de forma **dinâmica**, com
**três modos de entrada**: por **JSON**, por **link/URL** ou **manual** (formulário).
Todos produzem um `Product` em rascunho, validado pelo mesmo schema.

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/catalog/services.py::ProductRegistrar` |
| Teste | `backend/tests/catalog/test_product_registrar.py` |

## 3. Contrato

```python
class ProductDraftIn(BaseModel):
    """Schema canônico de um e-book a cadastrar (validação única dos 3 modos)."""
    title: str
    author: str
    description: str = ""
    price: Decimal
    category_slug: str | None = None
    cover_url: str | None = None
    file_url: str | None = None   # quando o arquivo vem por link


class ProductRegistrar:
    """Cadastra e-books a partir de JSON, link ou dados manuais."""

    def __init__(self, session: AsyncSession, importer: ManifestImporter) -> None:
        self.session = session
        self.importer = importer        # busca/parse de manifest por URL (abstração)

    async def from_json(self, payload: dict) -> Product:
        """Valida o JSON contra ProductDraftIn e cria o e-book (rascunho)."""

    async def from_link(self, url: str) -> Product:
        """Importa um manifest (JSON) de uma URL e cria o e-book (rascunho)."""

    async def from_fields(self, data: ProductDraftIn) -> Product:
        """Cria o e-book a partir de dados preenchidos manualmente."""
```

## 4. Dependências

| Depende de | Para quê | Nos testes |
|---|---|---|
| `AsyncSession` | persistência | real |
| `ManifestImporter` (Protocol) | baixar/parsear manifest de uma URL | **fake** (sem rede) |
| `model_product` | entidade | real |

## 5. Comportamento / regras

- **Produto é sempre e-book** → schema fixo (`ProductDraftIn`).
- Os 3 modos **convergem** para `ProductDraftIn` (validação única) → criam `status=draft`.
- `slug` gerado do título (único; sufixo se colidir).
- Modo **link**: a URL aponta para um **manifest JSON** (ou, futuramente, metadados a extrair);
  o `file_url`/`cover_url` podem apontar para os arquivos.
- Upload do arquivo do e-book e publicação são passos seguintes (admin).
- Validação de segurança da URL (somente http/https; evitar SSRF) — ver [`../../security/`](../../security/).

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | JSON válido | cria e-book rascunho |
| T2 | JSON inválido (sem preço) | erro de validação |
| T3 | Link com manifest válido (fake) | cria e-book rascunho |
| T4 | Link inacessível/sem http(s) | erro tratado (sem SSRF) |
| T5 | Manual válido | cria e-book rascunho |
| T6 | Título duplicado | slug recebe sufixo único |

## 7. Rastreabilidade

- Novo requisito (cadastro dinâmico) · Units: `model_product`, `router_admin_products`,
  `security/*` · UI: [`../../../frontend/`](../../../frontend/) (admin), fluxo em
  [`../../../flowcharts/navigation-admin.md`](../../../flowcharts/navigation-admin.md)

## 8. Pendências

- [ ] Modo link: manifest JSON vs extração de metadados de página.
- [ ] Proteção contra SSRF (allowlist de domínios?).
- [ ] Endpoint admin (`router_admin_products`) e proteção por papel (RBAC/JWT).
