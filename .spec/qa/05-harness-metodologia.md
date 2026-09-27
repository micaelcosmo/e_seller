# QA — O que é específico deste projeto

**Projeto:** e_seller · **Status:** vigente · **Motor:** 1.3.0
A metodologia do harness é a da skill `/qa` (`~/.claude/skills/qa/metodologia.md`,
espelhada em `.claude/skills/qa/metodologia.md`). Este documento registra **só o
que este projeto tem de diferente** — e, nesse recorte, manda sobre a metodologia.

## Ambiente

O QA roda numa **stack própria**, nunca na de desenvolvimento
([decisão D03](../decisoes-pendentes.yaml)):

```bash
python qa-harness/ambiente/stack.py subir    # confere portas livres, build, sobe e espera o app
python qa-harness/ambiente/stack.py estado   # portas, containers e saúde
python qa-harness/ambiente/stack.py descer   # para (mantém banco e arquivos)
python qa-harness/ambiente/stack.py zerar    # para e apaga os volumes de QA
python qa-harness/executar.py bootstrap      # depois de subir
```

- Projeto compose `eseller-qa` ([`qa-harness/ambiente/docker-compose.qa.yml`](../../qa-harness/ambiente/docker-compose.qa.yml)):
  `db` (Postgres 16), `backend` (mesmo Dockerfile do produto) e `frontend` (mesmo
  nginx do produto, que faz proxy de `/api/`, `/admin`, `/comprar`, `/pay/`, `/pedido/`).
  Sem túnel Cloudflare: nada do QA fica público.
- **Portas livres** ([D04](../decisoes-pendentes.yaml)): preferidas no `config.yaml`
  (frontend 48273, backend 48280, Postgres 48532), conferidas por conexão + `netstat`
  a cada subida; ocupada → próxima livre da faixa (48270-48279 / 48280-48289 /
  48530-48539) e o `config.yaml` é regravado. Tudo publicado só em `127.0.0.1`.
- `build` a cada subida: backend e frontend copiam o código para a imagem, então a
  stack de QA sempre reflete a árvore de trabalho.
- Integrações externas desligadas ([D07](../decisoes-pendentes.yaml)):
  `PAYMENT_PROVIDER=fake` (simulador local) e SMTP vazio. O que depende de Mercado
  Pago real ou de e-mail entregue é `[limitação de ambiente]`.
- **Nenhum `.env` é lido.** As variáveis do backend estão todas no compose de QA;
  segredos de infraestrutura e senhas das contas de QA são aleatórios, gerados na
  primeira subida em `qa-harness/ambiente/credenciais-locais.env` (fora do git,
  [D05](../decisoes-pendentes.yaml)). Nenhum valor desse arquivo é impresso.

## Autenticação do harness

- **API:** `Adaptador.autenticar` faz o login OAuth2 (formulário `username`/`password`) em
  `POST /api/v1/auth/token` **direto no backend** (porta `ambiente.backend`), para não gastar o
  limite de 10 logins/min por IP que o nginx concentra; a sessão `requests` leva o `Bearer` e as
  suítes chamam pelo nginx (a mesma origem que o navegador usa).
- **Navegador (SPA):** o SPA guarda a sessão no `localStorage` (`token`, `refresh_token`, `email`).
  `entrar_no_navegador` abre a loja, limpa o armazenamento, grava as três chaves e **sai para
  `about:blank`** — o próximo `abrir` carrega o SPA do zero já logado (sem isso, abrir `/#/...` a
  partir de `/` só troca o hash e o topo fica no estado sem sessão; ver histórico).
- **Navegador (painel `/admin`):** para o perfil `admin`, além do SPA, o adaptador preenche o
  formulário real do SQLAdmin em `/admin/login` (caminho de um administrador de verdade). Se o
  formulário não existe, a entrada é evidência inválida; se o login é recusado pelo produto, a
  jornada mostra e a conferência falha.
- Senhas das contas de QA: só em `credenciais-locais.env`; o adaptador lê e nunca imprime.
  Evidência de API sai com senha e token mascarados (`qa-harness/testes/api/base.py`, [D06](../decisoes-pendentes.yaml)).

## Massa de dados

`qa-harness/massa_de_dados.py`, direto no Postgres de QA (sem passar pelo código testado),
idempotente — apaga tudo que é de QA e recria:

| O quê | Contraste |
|---|---|
| `qa-cliente@eseller-qa.test` com pedido **pago** de `python-na-pratica` + `arquitetura-limpa-web` (posse + pagamento) | `qa-sem-compras@eseller-qa.test` só com pedido **pendente** (pendente não dá posse) |
| três links de download de `python-na-pratica`: válido, esgotado (5/5), expirado (ontem) | cada um prova uma regra do US-06 |
| avaliação **pendente** do cliente em `arquitetura-limpa-web` | fila de moderação × página pública |
| admin `qa-admin@eseller-qa.test` | semeado pelo próprio backend (`APP_ENV=dev`); a massa só confere |

Prefixos apagados a cada execução: e-mails `qa-%@eseller-qa.test` (e as contas `qa-novo-%` que as
jornadas criam), produtos `qa-%`, cupons `QA-%`, inscrições de newsletter `qa-%`. A `limpeza` de
jornada aceita `carrinho`, `favoritos`, `avaliacao` (do `slug`), `pedidos-pendentes` e `compras`
(pedidos da conta que contêm o `slug`) — isolada por jornada, para reexecução no healing.

## Fontes de verdade para as histórias

Ver [`../test/historias/_instrucao.md`](../test/historias/_instrucao.md): planejamento aprovado
(US/RF) → trilhas vivas (storefront, UXR, API, quality-bar) → telas e rotas reais → schema.
Quando planejamento e código divergem, o critério cita o planejamento e a divergência vira achado.

## Linhas do projeto

Nenhuma no `/qa completo`. A suíte pytest do backend (SQLite, ~500 testes, mais de 10 minutos)
fica fora de propósito: ela é o gate do desenvolvimento (TDD) e roda à parte
(`cd backend; .venv/Scripts/python.exe -m pytest`); o `/qa` prova o comportamento no Postgres
real, que é justamente onde os testes em SQLite não enxergam (QAF-01/02/03/16).

## Histórico do harness neste projeto

- **2026-09-27 — adoção (motor 1.2.2 → 1.3.0).** Stack própria `eseller-qa`, cadeia em `.spec/`,
  5 domínios (vitrine, acesso, compra, biblioteca, administração), 22 histórias, 53 pontos de
  integração, 20 jornadas, base visual de 4 perfis.
- **Estabilização antes da rodada 1:** erros de evidência vindos do próprio harness — corpo
  `application/problem+json` tratado como não-JSON (o `detail` sumia), cabeçalho lido com caixa
  errada, validade de avaliação que esperava campo inexistente. Corrigidos no teste.
- **Motor 1.3.0:** ação `teclar` criada na fonte global (busca do SPA só envia com Enter) — [D12](../decisoes-pendentes.yaml).
- **Rodada 1 (2026-09-27-0433) → healing 1 (2026-09-27-0457):** o adaptador deixava a aba em `/`
  depois de gravar a sessão; `abrir /#/...` só trocava o hash e o topo do SPA ficava sem sessão
  (biblioteca, favoritos, carrinho e pedidos como evidência inválida). Corrigido saindo para
  `about:blank`. Admin: navegação recusada era causa de **produto** (CSRF + `Host` sem porta).
- **Rodada 2:** o ponto de login do painel passou a enviar o `csrf_token` que a página do painel
  agora põe no formulário, com contraste sem token (403).
