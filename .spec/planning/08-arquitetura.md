# 08 — Arquitetura

> Documento de planning · e_seller · 2026-06-06 (revisado p/ FastAPI, serviços separados)
> Visão de componentes, responsabilidades e fluxos principais.

---

## 1. Visão geral (containers) — backend e frontend SEPARADOS

```
   ┌──────────────────────┐        HTTP/JSON        ┌────────────────────────────────┐
   │  frontend (serviço)  │ ──────────────────────► │  backend (FastAPI + Uvicorn)   │
   │  a definir; consome  │ ◄────────────────────── │   - API pública (catálogo,     │
   │  a API               │                         │     compra, pedido)            │
   └──────────────────────┘                         │   - Webhook Mercado Pago       │
                                                     │   - Download seguro (stream)   │
   ┌──────────────────────┐    navegador (P2)       │   - Painel admin (SQLAdmin)    │
   │  Admin (SQLAdmin)    │ ◄───────────────────────│     montado no backend         │
   └──────────────────────┘                         └───────┬───────────────┬────────┘
                                                             │               │
                                                     ┌───────▼──────┐ ┌──────▼─────────┐
                                                     │ db (Postgres)│ │ storage         │
                                                     │ produtos,    │ │ arquivos de     │
                                                     │ pedidos...   │ │ e-book (volume) │
                                                     └──────────────┘ └─────────────────┘
                                                             ▲
                                                             │ webhook (HTTPS)
                                                     ┌───────┴────────┐
                                                     │  Mercado Pago  │ (externo)
                                                     └────────────────┘
```

> **Separação:** `frontend` e `backend` são serviços/containers independentes,
> que conversam **só por HTTP/JSON**. O frontend pode ser trocado sem tocar no backend.
> O **catálogo é renderizado pelo frontend** consumindo a API (não há páginas
> server-rendered no backend). O **admin (SQLAdmin)** é montado no próprio backend
> para o MVP (ADR-008).

## 2. Organização interna do backend (módulos)

> 💡 *No FastAPI não há "apps" como no Django.* Organizamos por **módulos de domínio**,
> cada um com seus `router`, `schemas` (Pydantic), `services` (regras) e `models` (SQLAlchemy).

```
app/
├─ core/        # config, sessão do DB, segurança (JWT), healthcheck
├─ catalog/     # produtos, categorias
├─ orders/      # pedido (Order), máquina de estados
├─ payments/    # integração Mercado Pago (checkout + webhook)
├─ delivery/    # link seguro, expiração/limite, download (stream)
├─ accounts/    # autenticação de admin
└─ admin/       # montagem do SQLAdmin
```

| Módulo | Responsabilidade |
|---|---|
| `catalog` | Produtos (e-books), categorias, listagem e detalhe (API). |
| `orders` | Pedido (Order), itens, máquina de estados. |
| `payments` | Mercado Pago: criar checkout e processar webhook. |
| `delivery` | Geração de link seguro, expiração/limite, download. |
| `accounts` | Autenticação de admin (JWT). |
| `core` | Config, sessão de DB, segurança, healthcheck. |
| `admin` | Painel SQLAdmin (CRUD para P2). |

## 3. Camadas (dentro de cada módulo)

```
router (HTTP/FastAPI)
   │   valida entrada/saída com schemas Pydantic
   ▼
service (regras de negócio)      ← onde mora a lógica testável
   │
   ├─► models/repository (SQLAlchemy)   ← persistência
   └─► gateways externos (ex.: cliente Mercado Pago)  ← mockável nos testes
```

- **Regras de negócio nos *services***, não nos routers — testar sem HTTP.
- **Schemas Pydantic** definem o contrato de entrada/saída da API.
- **Models SQLAlchemy** cuidam de persistência e invariantes simples.
- **Clientes externos** isolados (ex.: `payments/gateways/mercadopago.py`) para *mockar*.

## 4. Fluxo crítico — pagamento e entrega

```
1. Frontend envia compra            → POST /api/orders  → orders.services.create_order() [pendente]
2. Backend cria checkout            → payments.services.create_checkout()
3. Cliente paga no Mercado Pago
4. Mercado Pago chama o webhook      → POST /api/webhooks/mercadopago (payments.router)
5. Webhook valida + é idempotente    → payments.services.process_notification()
6. Pedido vira "pago"                → orders.services.mark_paid()
7. Link de download gerado           → delivery.services.issue_download()
8. Cliente baixa                     → GET /api/download/{token} (valida token/limite, faz stream)
```

> Detalhes de idempotência e estados em [`09-modelo-de-dominio.md`](09-modelo-de-dominio.md);
> segurança do download em [`20-entrega-ebook-anti-pirataria.md`](20-entrega-ebook-anti-pirataria.md);
> contratos em [`11-contratos-api.md`](11-contratos-api.md).

## 5. Decisões transversais

- **Configuração por ambiente** via variáveis de ambiente (12-factor), lidas por `pydantic-settings`.
- **Segredos** fora do repositório (`.env`, cofre na produção).
- **Migrations (Alembic)** versionadas no Git.
- **Idempotência** no webhook como requisito de design.
- **CORS** configurado no backend para aceitar o domínio do frontend (serviços separados).

## 6. Pendências

- [ ] Services **sync** ou **async** (depende do driver Postgres — ADR-003/008).
- [ ] Tarefas assíncronas (ex.: e-mail)? Avaliar **Celery/RQ + Redis** (open-source) — fora do MVP.
- [ ] Storage: volume Docker local no MVP; objeto (S3-compatível) depois.
- [ ] Admin junto do backend (SQLAdmin) vs no frontend (ADR-008).
