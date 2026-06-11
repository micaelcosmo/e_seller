# Unit: ports (`infra`) — mapa de portas

> Tipo: `infra` · Área: `infra`
> Deriva de: decisão do Micael (2026-06-07) · Padrões: [`../standards/`](../../standards/) · Status: **Rascunho**

---

## 1. Objetivo

Definir **portas não-padrão** para todos os serviços, evitando conflito com outras
aplicações do Micael (que usam as portas padrão e algumas logo acima).

## 2. Mapa de portas (base `48xxx`)

> Faixa privada/dinâmica (49152+ é "dynamic"; usamos 48xxx, alto e improvável de colidir).
> **Todas configuráveis por variável de ambiente** (valores abaixo são o default).

| Serviço | Porta (host) | Env | Observação |
|---|---|---|---|
| Backend API (Uvicorn/Gunicorn) | **48080** | `BACKEND_PORT` | substitui 8000 |
| PostgreSQL | **48432** | `POSTGRES_PORT` | substitui 5432 |
| Frontend (storefront) | **48173** | `FRONTEND_PORT` | substitui 5173/3000 |
| Dashboard (self_reflection) | **48088** | `DASHBOARD_PORT` | observabilidade da evolução |

> Dentro da rede Docker os serviços se falam pelas portas internas padrão; o **mapeamento
> de host** é que usa as portas acima (ex.: `48080:8000`). Em produção/túnel, ver
> [`../../distribution/`](../../distribution/).

## 3. Regras

- Nunca hardcodar porta no código; ler de env (ver [`env_config`](env_config.md)).
- Documentar qualquer porta nova aqui antes de usar.
- O Cloudflare Tunnel aponta para a porta do backend/frontend (ver distribuição).

## 4. Casos de teste / verificação

| # | Cenário | Esperado |
|---|---|---|
| T1 | `docker compose up` | serviços expostos nas portas 48xxx |
| T2 | Conflito com app do Micael | nenhum (portas distintas) |

## 5. Pendências

- [ ] Confirmar que nenhuma 48xxx está em uso na máquina do Micael.
