# Histórias de Usuário — Acesso e conta

**Status:** vigente · **Derivado de:** `.spec/planning/03-requisitos-funcionais.md` (RF-50, RF-52) · `.spec/frontend/storefront.md` §1 (login/cadastro do comprador) · `.spec/enrichment/roadmap-aaa.md` (blacklist de token) · `.spec/unit/backend/billing/router_billing.md` · telas modal `#auth-modal` (`setupAuth`) e `#/conta` (`renderAccount`) em `frontend/public/app.js` · rotas `/api/v1/auth/*`, `/api/v1/billing/profile` · **Instrução:** `_instrucao.md`
**Jornadas:** `.spec/test/jornadas/acesso.yaml`

## História 1 - Visitante cria uma conta de comprador
**Como** visitante, **quero** criar uma conta com nome, e-mail e senha, **para** ter biblioteca, favoritos e histórico de compras.
**Fontes:** `.spec/frontend/storefront.md`:§1 (`/cadastro`) · RF-52 · modal `#auth-modal` aba "Criar conta" · `POST /api/v1/auth/register`
**Critérios de aceite:**
- [ ] Criar conta pelo modal já entra na conta: o topo passa a mostrar Biblioteca, Pedidos e Conta (fonte: storefront.md §1; `setupAuth`)
- [ ] E-mail já cadastrado é recusado com a mensagem "E-mail já cadastrado" (fonte: `backend/app/core/exception_handlers.py`, contrato 409)

## História 2 - Comprador entra e sai da conta
**Como** comprador, **quero** entrar com meu e-mail e senha e sair quando terminar, **para** usar a loja com segurança.
**Fontes:** `.spec/frontend/storefront.md`:§1 (`/login`) · RF-52 · `.spec/enrichment/roadmap-aaa.md` (logout revoga o token) · modal `#auth-modal` aba "Entrar" · `POST /api/v1/auth/token`, `POST /api/v1/auth/logout`
**Critérios de aceite:**
- [ ] Entrar com e-mail e senha corretos libera Biblioteca, Pedidos e Conta no topo (fonte: storefront.md §1)
- [ ] Senha errada é recusada com "Credenciais inválidas" (fonte: `backend/app/accounts/router.py`, contrato 401)
- [ ] Sair da conta volta o topo para o botão "Entrar" (fonte: `setupAuth`)
- [ ] Depois do logout na API, o mesmo token não é mais aceito (fonte: roadmap-aaa.md, blacklist)

## História 3 - Comprador mantém o perfil fiscal
**Como** comprador, **quero** salvar meus dados fiscais (tipo de pessoa, nome, CPF, endereço), **para** receber a nota da compra.
**Fontes:** `.spec/unit/backend/billing/router_billing.md` (T1, T2) · tela `#/conta` (`renderAccount`, botão "Salvar perfil") · `PUT /api/v1/billing/profile`
**Critérios de aceite:**
- [ ] Salvar o perfil com Pessoa Física, nome, CPF e endereço confirma "Perfil salvo!" (fonte: router_billing.md T1)
- [ ] Sem login a API recusa o perfil fiscal (401) (fonte: router_billing.md T2)
