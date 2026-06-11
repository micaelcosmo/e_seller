# Fluxograma — Navegação do Vendedor/Admin

> Trilha flowcharts · e_seller · 2026-06-07

```mermaid
flowchart TD
    L[Login admin - JWT] --> D[Painel]
    D --> PROD[Produtos - e-books]
    D --> PED[Pedidos / Pagamentos]
    D --> REL[Relatorios de vendas]
    D --> CUP[Cupons - tier]

    PROD --> NOVO[Cadastrar novo e-book]
    NOVO --> M1[Modo JSON: colar JSON]
    NOVO --> M2[Modo Link: importar de URL]
    NOVO --> M3[Modo Manual: preencher formulario]
    M1 --> VAL{Validacao do schema do e-book}
    M2 --> VAL
    M3 --> VAL
    VAL -- ok --> SALVA[Salva como rascunho]
    VAL -- erro --> NOVO
    SALVA --> UP[Upload do arquivo + capa]
    UP --> PUB[Publicar]
    PUB --> CAT[Aparece no catalogo]

    PED --> VER[Ver detalhe / status]
    VER --> EST[Estorno - tier]
```

> O **produto é sempre um e-book** (schema fixo). O cadastro é **dinâmico** com 3 modos
> de entrada (JSON / link / manual) — ver requisito em [`../checklist.md`](../checklist.md)
> e a unit [`../unit/backend/catalog/service_create_product.md`](../unit/backend/catalog/service_create_product.md).
