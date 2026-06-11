# Alternativas de Distribuição

> Trilha distribution · e_seller · 2026-06-07

---

## Comparação (PC como servidor, custo zero/baixo)

| Opção | Prós | Contras |
|---|---|---|
| **Cloudflare Tunnel** (principal) | HTTPS grátis, URL estável c/ domínio, Access p/ proteger admin, sem abrir portas | requer conta CF p/ túnel nomeado |
| **ngrok** | setup rápido, ótimo p/ testes/webhook | URL estável é paga; limites no grátis |
| **Tailscale Funnel** | simples, seguro (rede privada + funnel público) | ecossistema Tailscale; menos "domínio próprio" |
| **Port forwarding no roteador** | direto | expõe a rede, sem HTTPS automático, exige IP fixo/DDNS — **não recomendado** |

## Recomendação

- **Cloudflare Tunnel nomeado** para o uso real (webhook precisa de URL estável).
- **ngrok** ou `cloudflared --url` para testes pontuais.

## Pendências

- [ ] Confirmar conta/domínio Cloudflare.
