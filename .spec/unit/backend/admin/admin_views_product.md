# Unit: ProductAdmin / CategoryAdmin (`admin`)

> Tipo: `admin` view · Área: `backend/admin`
> Deriva de: RF-10,11,12,13 · ADR-008 · Padrões: [`../../../standards/`](../../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

CRUD administrativo de produtos e categorias via SQLAdmin (P2).

## 2. Localização

| Item | Caminho |
|---|---|
| Código | `backend/app/admin/views.py` (`ProductAdmin`, `CategoryAdmin`) |
| Teste | `backend/tests/admin/test_admin_product.py` |

## 3. Contrato

```python
class ProductAdmin(ModelView, model=Product):
    column_list = [Product.title, Product.price, Product.status]
    # upload do arquivo + capa; validação de tipo/tamanho


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.name, Category.slug]
```

## 4. Dependências

| Depende de | Para quê |
|---|---|
| `catalog/model_product`, `model_category` | dados |
| `security/file_protection` | salvar arquivo em volume protegido |

## 5. Comportamento / regras

- Upload valida **tipo** (PDF/EPUB) e **tamanho** (RF-12).
- Arquivo salvo no volume protegido (não público) — RNF-03.
- Publicar exige `file` presente.

## 6. Casos de teste (TDD)

| # | Cenário | Esperado |
|---|---|---|
| T1 | Criar produto válido | salva como rascunho |
| T2 | Upload de tipo inválido | erro de validação |
| T3 | Publicar sem arquivo | bloqueado |

## 7. Rastreabilidade

- RF-10,11,12,13 · US-03 · Units: `catalog/model_product`, `security/file_protection`

## 8. Pendências

- [ ] Limite de tamanho do upload.
