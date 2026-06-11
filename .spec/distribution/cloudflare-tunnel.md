# Distribuição via Cloudflare Tunnel

> Trilha distribution · e_seller · 2026-06-07 · Status: **Rascunho**

---

## 1. Ideia

O **Cloudflare Tunnel** (daemon `cloudflared`) cria um túnel de saída do PC do Micael
até a borda da Cloudflare, publicando um **link HTTPS** acessível de qualquer lugar
(PC/celular) — **sem abrir portas no roteador** e sem IP fixo.

```
Celular/PC (internet) → https://<link>.trycloudflare.com (ou domínio CF)
        → Cloudflare edge → cloudflared (PC do Micael) → backend :48080 / frontend :48173
```

## 2. Por que essa opção

- **Custo zero** (plano gratuito; `trycloudflare` para testes rápidos, domínio próprio se quiser).
- HTTPS automático (TLS na borda).
- Não expõe a rede local diretamente; o PC só faz conexão de **saída**.

## 3. Como funciona (passos — runbook resumido)

1. Instalar `cloudflared` no PC.
2. Subir o app via Docker (backend `48080`, frontend `48173` — ver [`../unit/infra/ports.md`](../unit/infra/ports.md)).
3. Rodar o túnel apontando para o serviço público (frontend ou backend):
   - Teste rápido: `cloudflared tunnel --url http://localhost:48173`.
   - Persistente: túnel **nomeado** + arquivo de config + (opcional) domínio próprio.
4. Compartilhar o link gerado.

> O runbook operacional detalhado vive em [`../ops/`](../ops/) quando formos executar.

## 4. O que expor (e o que NÃO expor)

| Serviço | Exposto no túnel? |
|---|---|
| Frontend (storefront) | ✅ público |
| Backend API (rotas públicas) | ✅ (idealmente sob o mesmo domínio/caminho) |
| Webhook do Mercado Pago | ✅ (precisa de URL pública estável — usar **túnel nomeado**, não `trycloudflare` efêmero) |
| **Admin (SQLAdmin)** | ⚠️ restringir — **Cloudflare Access** / IP allowlist / não publicar |
| **PostgreSQL / Dashboard** | ❌ nunca público |

## 5. Segurança

- Webhook precisa de URL **estável** → túnel nomeado com domínio (efêmero quebra a config no Mercado Pago).
- Proteger `/admin` com **Cloudflare Access** (login) ou não roteá-lo pelo túnel.
- `APP_ALLOWED_ORIGINS`/CORS apontando para o domínio do túnel.
- Segredos seguem em env/cofre (RNF-04). Ver [`../security/threat-model.md`](../security/threat-model.md).

## 6. Limitações (fase PC-as-server)

- O app só responde **com o PC ligado** e `cloudflared` rodando.
- Latência/disponibilidade dependem da conexão do PC.
- Plano de evolução: migrar para hospedagem de baixo custo ([`../roadmap.md`](../roadmap.md) M16/produção).

## 7. Pendências

- [ ] Túnel efêmero (teste) vs nomeado + domínio (webhook estável).
- [ ] Proteger o admin (Cloudflare Access?).
- [ ] Roteamento: um host para frontend, caminho `/api` para backend.
