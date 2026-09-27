# Decisões pendentes — para você analisar depois das rodadas

**Gerado em:** 2026-09-27 · **Fonte:** [`decisoes-pendentes.yaml`](decisoes-pendentes.yaml) (este arquivo é o resumo)
**Como usar:** comece pelas ⚠️ **bloqueantes** — elas **não** foram implementadas e esperam você.
As outras já estão feitas e são reversíveis; a coluna "Se você discordar" diz o que muda.
Quando decidir, troque o `status` no `.yaml` para `aprovada` ou `revertida` (o histórico fica).

## Em uma frase

Montei o `/qa` no e_seller numa **stack de QA separada** (portas livres, sem ler `.env`, senhas
aleatórias fora do git), bloqueei o Claude de fazer `git add/commit/push`, rodei o QA, corrigi o
que ele provou (backend, nginx e SPA) e dei o **tapa visual em Material 3** mantendo o roxo e o
laranja. Ficaram **5 decisões bloqueantes** para você.

## ⚠️ Bloqueantes (não implementadas — aguardando você)

| # | O que decidir | Por que travou | Opções |
|---|---|---|---|
| ⚠️ D18 | **Painéis HTML de admin** (`/api/v1/admin/*/panel`: pedidos, cupons, downloads, usuários, cadastro) não abrem no navegador — pedem cabeçalho `Authorization` | é escolha de produto do painel | (a) aceitar a sessão do `/admin` nesses painéis · (b) aposentar e ficar só no SQLAdmin · (c) virar tela do SPA |
| ⚠️ D19 | **Limite de login por IP atrás do nginx/túnel**: o backend vê todo mundo com o IP do nginx — 10 logins/min para o site inteiro; e o HTTPS do túnel não chega ao backend | mexe em confiança de proxy (segurança) | confiar em `X-Forwarded-For/Proto` só da rede do compose · manter |
| ⚠️ D20 | `docker-compose.yml` de dev: `DATABASE_URL` aponta `e_seller2`, `POSTGRES_DB` cria `e_seller` — **volume novo não sobe** | mudar mexe no banco que você usa | alinhar em `e_seller2` · alinhar em `e_seller` e migrar |
| ⚠️ D21 | **Política de privacidade diz "Argon2"**, o sistema usa PBKDF2 | é texto jurídico | corrigir o texto · migrar para Argon2 |
| ⚠️ D22 | **Pagamento real**: não existe gateway do Mercado Pago no código (o simulador `fake` está fixo) | precisa das credenciais | implementar o gateway quando houver conta |

## Feitas (reversíveis)

| # | Decisão | Por que escolhi | Se você discordar |
|---|---|---|---|
| D01 | Bloqueio de `git add/commit/push` e de leitura de `.env` no `.claude/settings.json` do projeto (deny + hook testado com 14 casos) | vale em qualquer sessão neste repo | mover para `settings.local.json` ou para o global |
| D02 | Hook conservador (barra até texto que só menciona `git commit`) | falso positivo é barato; commit indevido não | parser de shell mais preciso |
| D03 | QA numa **stack própria** `eseller-qa` (sem túnel) | a massa apaga/recria dados; nada público | rodar na stack de dev |
| D04 | Portas de QA 48273/48280/48532 (faixas 4827x/4828x/4853x), trocadas sozinhas se ocupadas | previsível e longe das de dev | porta aleatória (exige mudar a skill) |
| D05 | **Senhas de QA aleatórias** em `credenciais-locais.env` (fora do git) | zero senha no git | senhas fixas no config (vão para o git) |
| D06 | Evidência de API com **senha e token mascarados** pelo projeto | o motor gravava tudo cru | levar o mascaramento para o motor global |
| D07 | Mercado Pago e SMTP desligados no QA (simulador `fake`) | sem credenciais e sem ler `.env` | sandbox (você fornece credenciais) |
| D08 | Identificadores do `qa-harness/` em português | casa com o motor da skill | reescrever em inglês |
| D09 | Cadeia de QA em `.spec/` (não `spec/`) | uma árvore de spec só | `spec/` separado |
| D10 | CLAUDE.md §4 atualizado para a fase real (Enrichment + QA) | a regra antiga proibia código | voltar o texto |
| D11 | O motor da skill lê `.env` da raiz **se existir** (hoje não existe) | não há leitura hoje | mudar o motor global |
| D12 | Ação **`teclar`** no motor global da skill (1.2.2 → 1.3.0) | a busca só envia com Enter | voltar para 1.2.2 |
| D13 | Login do `/admin` com **CSRF mantido** (script no template do SQLAdmin) | segurança preservada | isentar `/admin` do CSRF |
| D14 | Moderação de avaliações pelo painel (edição **só do status**) | a história pede tela | só pela API |
| D15 | Páginas do backend (pagamento, pedido, institucionais) no **tema claro** da loja | o checkout parecia outro site | voltar ao escuro do FEV |
| D16 | Visual sem fonte externa (fontes do sistema) | leve e custo zero | hospedar Inter/Roboto Flex |
| D17 | Botão de **buscar** visível (Enter continua) | ação explícita no celular | só Enter |
| D23 | Migration Alembic do `reviewstatus` diverge do ORM (registrado, sem mudança) | o boot usa `create_all` | nova migration / Alembic no boot |
| D24 | Senha descartável `qa-senha-{{execucao}}` nas jornadas de cadastro/login | conta criada e apagada pela própria execução | gerar e ler de arquivo local |
| D25 | Evidências de imagem (~58 MB de base64) propostas num **commit separado e opcional** | não decidir por você o peso do repo | só relatórios no git · Git LFS |

## Achados do QA e o que foi feito

Detalhe em [`enrichment/roadmap-qaf.md`](enrichment/roadmap-qaf.md) e nos relatórios em
[`../qa-harness/relatorios/`](../qa-harness/relatorios/). **18 achados corrigidos com teste**, entre eles:
backend não subia num Postgres novo; busca e **download davam 500 no Postgres**; **e-book novo
cadastrado pelo admin não era entregue a quem comprava**; "Comprar e baixar" não levava ao pagamento;
perfil fiscal nunca salvava; painel `/admin` inacessível (CSRF + porta); páginas de pagamento sem
estilo; cupom em minúsculas; "Pagar" ausente; favoritar dava 500.

| Execução | Válidos | Falha de produto | Evidência inválida |
|---|---|---|---|
| Rodada 1 (2026-09-27-0433) | 53 | 16 | 9 → healing |
| Rodada 2 (2026-09-27-0521) | 75 | 3 | 0 |
| Rodada 3 (2026-09-27-0547) | 78 | 1 (D18) | 0 |
| Rodada 4 (2026-09-27-0610) | 78 | 1 (D18) | 0 |

A falha que sobra é a base visual do admin: os painéis HTML da **D18** (bloqueante, esperando você).
