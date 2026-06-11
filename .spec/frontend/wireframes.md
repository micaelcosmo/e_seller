# Wireframes — e_seller

> DOC-03 · Frontend · 2026-06-10

Telas principais em ASCII art para referência de layout e fluxo.

---

## 1. Home / Catálogo

```
┌──────────────────────────────────────────────────────────┐
│ 📚 e_seller  [Buscar e-books…]      🛒 📚 Conta  Entrar │
├──────────────────────────────────────────────────────────┤
│              E-books, na hora.                           │
│    Compre, pague e baixe em segundos. Simples assim.     │
├──────────────────────────────────────────────────────────┤
│ Filtros: [Todos] [Python] [FastAPI] [Arquitetura]        │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│ │  [capa]  │ │  [capa]  │ │  [capa]  │ │  [capa]  │    │
│ │ Título   │ │ Título   │ │ Título   │ │ Título   │    │
│ │ Autor    │ │ Autor    │ │ Autor    │ │ Autor    │    │
│ │ R$ 39,90 │ │ R$ 49,90 │ │ R$ 59,90 │ │ RASCUNHO │    │
│ │[Comprar] │ │[Comprar] │ │[Comprar] │ │          │    │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
├──────────────────────────────────────────────────────────┤
│ [E-mail para newsletter]              [Assinar]          │
│ e_seller · demo · API | Privacidade · Termos de uso      │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Página do Produto

```
┌──────────────────────────────────────────────────────────┐
│ 📚 e_seller  [Buscar…]              🛒 📚 Conta  Entrar │
├──────────────────────────────────────────────────────────┤
│ ← Voltar ao catálogo                                     │
│ ┌──────────────┐  Título do E-book                       │
│ │              │  Autor · tag1 · tag2                    │
│ │   [CAPA]     │  Descrição detalhada do e-book…         │
│ │              │                                         │
│ │              │  R$ 49,90                               │
│ └──────────────┘                                         │
│                   ┌─────────────────────────────────┐    │
│                   │ Comprar agora                   │    │
│                   │ [seu@email.com            ]     │    │
│                   │ [Cupom (opcional)         ]     │    │
│                   │ [Comprar e baixar] [🛒 Carrinho]│    │
│                   └─────────────────────────────────┘    │
├──────────────────────────────────────────────────────────┤
│ Avaliações                                               │
│ ★★★★☆  Comprador A — Excelente!                         │
│ ★★★★★  Comprador B — Recomendo muito.                   │
│ [★★★★★ ▼] [Seu comentário…]  [Avaliar]                  │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Checkout / Pagamento (simulado)

```
┌──────────────────────────────────────────────────────────┐
│ Simulador de Pagamento — e_seller (modo dev)             │
├──────────────────────────────────────────────────────────┤
│  Pedido: #ABC123                                         │
│  Produto: FastAPI do Zero                                │
│  Valor: R$ 49,90                                         │
│                                                          │
│  Simular resultado:                                      │
│  [ Aprovado ] [ Recusado ] [ Pendente ]                  │
│                                                          │
│  [    CONFIRMAR    ]                                     │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Modal de Login / Registro

```
┌────────────────────────────┐
│ ×                          │
│ [Entrar]  [Criar conta]    │
│ ─────────────────────────  │
│ [Nome completo (registro)] │
│ [seu@email.com           ] │
│ [Senha (mín. 6 caracteres)]│
│                            │
│ [  Erro de validação...  ] │
│                            │
│ [        Entrar           ]│
│                            │
│ Ao criar conta, você       │
│ concorda com os Termos     │
│ de uso e Privacidade.      │
└────────────────────────────┘
```

---

## 5. Minha Biblioteca

```
┌──────────────────────────────────────────────────────────┐
│ 📚 Minha Biblioteca                                      │
├──────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐                                │
│ │  [capa]  │ │  [capa]  │                                │
│ │ Título 1 │ │ Título 2 │                                │
│ │[⬇️ Baixar]│ │[⬇️ Baixar]│                                │
│ └──────────┘ └──────────┘                                │
└──────────────────────────────────────────────────────────┘
```

---

## 6. Painel Admin — Cadastro de E-book (3 modos)

```
┌──────────────────────────────────────────────────────────┐
│ Cadastrar E-book                                         │
│ ← Voltar ao painel | Publicação                          │
├──────────────────────────────────────────────────────────┤
│ [Manual ●] [JSON] [Link/URL]                             │
├──────────────────────────────────────────────────────────┤
│ Modo manual:                                             │
│  Título *  [                                    ]        │
│  Preço *   [29.90                               ]        │
│  Autor     [                                    ]        │
│  Descrição [                                    ]        │
│  URL capa  [https://...                         ]        │
│                                    [  Cadastrar  ]       │
├──────────────────────────────────────────────────────────┤
│  ✅ Cadastrado: FastAPI do Zero (slug: fastapi-do-zero)  │
└──────────────────────────────────────────────────────────┘
```

---

## 7. Painel Admin — Publicação

```
┌──────────────────────────────────────────────────────────┐
│ Publicação de e-books                                    │
│ ← Voltar ao painel                                       │
├─────┬──────────────────────┬─────────────┬──────────────┤
│ ID  │ Título               │ Status      │ Ação         │
├─────┼──────────────────────┼─────────────┼──────────────┤
│  1  │ Python na Prática    │ ● Publicado │ [Despublicar]│
│  2  │ FastAPI do Zero      │ ● Publicado │ [Despublicar]│
│  3  │ Arquitetura Limpa    │ ○ Rascunho  │ [Publicar]   │
└─────┴──────────────────────┴─────────────┴──────────────┘
```

---

*Nota: wireframes ASCII servem de referência para o layout; a implementação usa CSS flex/grid real.*
