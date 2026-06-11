# Fluxograma — Navegação do Cliente (comprador)

> Trilha flowcharts · e_seller · 2026-06-07

```mermaid
flowchart TD
    H[Home / Landing] --> CAT[Catalogo de e-books]
    H --> BUSCA[Busca]
    CAT --> DET[Detalhe do e-book]
    BUSCA --> DET
    DET --> AUTH{Logar ou continuar como convidado?}
    AUTH -- Login/Cadastro --> CONTA[Conta do leitor]
    AUTH -- Convidado --> EMAIL[Informa e-mail]
    CONTA --> CHECK[Checkout]
    EMAIL --> CHECK
    CHECK --> PAY[Pagamento - Mercado Pago]
    PAY -->|aprovado| OK[Pedido pago]
    OK --> DL[Download seguro]
    OK --> BIB[Minha Biblioteca - se logado]
    PAY -->|recusado| FAIL[Tentar novamente]
    CONTA --> BIB
    BIB --> DL
    DET --> WISH[Adicionar a wishlist - se logado]
```

> Inclui os requisitos novos: **home/landing** e **login do comprador** (opcional;
> compra como convidado continua possível). Biblioteca/wishlist exigem login.
