# Roadmap QAF — Ajustes do QA (rodadas do `/qa`)

> Épico **QAF**. Nasce dos achados (FALHA DE PRODUTO) das rodadas do `/qa`
> ([`qa-harness/relatorios/`](../../qa-harness/relatorios/)). Início: 2026-09-27.
> Fluxo de cada item: **spec (este arquivo) → teste que falha → correção → teste verde → `/qa` valida**.
> Decisão que depende do dono **não** entra aqui: fica em [`../decisoes-pendentes.yaml`](../decisoes-pendentes.yaml).

---

## Princípios

1. **Só o que o QA provou.** Cada item cita o ponto/jornada da rodada que o evidenciou.
2. **Menor mudança que fecha o achado**, sem refatoração oportunista.
3. **Teste de regressão no nível certo:** regra de backend → pytest (`backend/tests/test_qaNN_*.py`);
   roteamento do nginx e comportamento do SPA → ponto/jornada do `/qa` (não há runner de JS no projeto).
4. **Postgres é o banco real.** Os testes usam SQLite; achado que só existe no Postgres ganha
   teste que reproduz a diferença (tipo com fuso, SQL compilado para o dialeto) — nunca só "passa no SQLite".

---

## Itens

| ID | Achado (evidência) | Correção | Teste |
|---|---|---|---|
| QAF-01 | Backend **não sobe** num Postgres novo: `server_default='pending'` no enum `reviewstatus` (bootstrap da stack de QA) | `server_default` = nome do membro (`PENDING`) | `test_qa01_enum_server_default.py` (DDL de todas as colunas enum) |
| QAF-02 | **Busca dá 500 no Postgres** (`SELECT DISTINCT` + `ORDER BY CASE` de relevância) — vitrine Ponto 3 | ordenar por relevância sem `DISTINCT` (sem join que duplique) ou com a expressão no select | pytest: SQL compilado para Postgres não pode ter `DISTINCT` com `ORDER BY` fora do select |
| QAF-03 | **Todo download dá 500 no Postgres** (`expires_at` com fuso × `Clock.now()` sem fuso) — biblioteca Pontos 3–5 | comparar em UTC normalizado (fuso removido nos dois lados) | pytest: `consume` com `expires_at` *aware* (como o Postgres devolve) — válido, expirado, esgotado |
| QAF-04 | Lista de pedidos do admin **sem data** (US-07) — administração Ponto 7 | `created_at` (e `buyer_email`) no item da lista | pytest: `GET /api/v1/orders` traz `created_at` |
| QAF-05 | Pedido pendente sem `checkout_url` em "Meus pedidos" (RF-25) — compra Ponto 11 | `checkout_url` recalculado para pedido pendente em `/orders/my` e `/orders/{ref}` | pytest: pendente traz `checkout_url`; pago não traz |
| QAF-06 | Cupom em minúsculas: prévia diz válido, pedido recusa — compra Ponto 10 | código do cupom normalizado (sem espaço, maiúsculo) na busca do serviço | pytest: pedido com `bemvindo10` aplica 10% |
| QAF-07 | "Comprar e baixar" **não leva ao pagamento** (US-04) — jornada `visitante-compra-sem-conta` | SPA vai para o `checkout_url` do pedido criado | `/qa` (jornada) |
| QAF-08 | Perfil fiscal **nunca salva**: SPA manda `PF/PJ`, API espera `individual/company` — acesso Ponto 6 | SPA envia/lê os valores do contrato da API | `/qa` (ponto + jornada) |
| QAF-09 | nginx devolve o SPA para `/static/`, `/privacidade`, `/termos` — simulador/pedido **sem estilo**, rodapé leva à home — compra Ponto 4, vitrine Pontos 8–9 | `location` de proxy para essas rotas | `/qa` (pontos + base visual) |
| QAF-10 | Login do painel `/admin` barrado pelo CSRF (403) — administração Ponto 3 | formulários do SQLAdmin passam a enviar o `csrf_token` (double-submit mantido) | pytest: login do SQLAdmin com o token do cookie → 302 para `/admin/`; sem token → 403 |
| QAF-11 | Lista de avaliações do painel sem comentário nem status (moderação às cegas) — jornada `administrador-ve-a-fila-de-moderacao` | `comment`, `status` e data na lista, filtro por status (`StaticValuesFilter`), edição só do status; comentário resumido e data curta (sem estourar a largura no notebook — `/qa responsividade`) | pytest: lista **renderizada** logado (200, com o comentário e com filtro) e formatadores |
| QAF-12 | Link "Admin" do topo **nunca aparece** (SPA lê `role` que o JWT não tem) | SPA consulta `/api/v1/auth/me` para decidir | `/qa` (base visual do admin) |
| QAF-13 | nginx repassa `Host $host` (sem porta): SQLAdmin redireciona e carrega estáticos em `:80` — painel em branco (base visual do admin, console) | `proxy_set_header Host $http_host` | `/qa` (jornadas do admin) |
| QAF-14 | `POST /comprar` (vitrine do backend) quebrava com `TypeError` (`OrderCreator` sem `coupons`) — escondido porque o CSRF consumia o corpo do formulário | CSRF guarda o corpo (`request.body()`) antes de ler o formulário; `OrderCreator` recebe o `CouponService` | pytest: `/comprar` com token → 303 para o simulador |
| QAF-15 | Título da aba fica "Python na Prática — e_seller" depois de sair do e-book (base visual do visitante) | SPA volta ao título original do `index.html` fora do detalhe | `/qa` (métrica `titulo_da_pagina` da base visual) |
| QAF-16 | Favoritar dá **500** no Postgres: o SPA liga o coração duas vezes (dois POST) e o serviço confere-e-insere (corrida → UNIQUE) — console da jornada de favoritos | serviço idempotente na corrida (savepoint + `IntegrityError`); SPA liga cada botão uma vez | pytest: segundo `add` com a conferência atrasada não quebra |
| QAF-17 | `backend/.env.example` com `DATABASE_URL=sqlite:///...` (driver síncrono que o `create_async_engine` recusa) | `sqlite+aiosqlite:///./e_seller.db` | leitura (arquivo de exemplo) |
| QAF-23 | **E-book novo cadastrado pelo admin não era entregue** (404 "Arquivo indisponível"): o upload grava `ProductFile` primário, o download lia só `Product.file_name` (seed) — administração Ponto 14 | download usa o arquivo primário; `file_name` só como alternativa | pytest: streamer entrega o `ProductFile` primário com nome `slug.ext` |

---

## Fora deste épico (decisão do dono)

Ver [`../decisoes-pendentes.md`](../decisoes-pendentes.md): painéis HTML em `/api/v1/admin/*/panel`
que só abrem com cabeçalho `Authorization`; banco padrão do `docker-compose.yml` de dev
(`e_seller2` × `POSTGRES_DB=e_seller`); limite de login por IP atrás do nginx (todo mundo com o
mesmo IP); texto da política de privacidade que cita Argon2 (o produto usa PBKDF2).
