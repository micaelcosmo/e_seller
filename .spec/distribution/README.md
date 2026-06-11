# .spec/distribution/

Trilha **viva** de **distribuição/acesso**: como o e_seller fica acessível por um
**link** (computador e celular), com a máquina do Micael atuando como **servidor**
por enquanto.

## Documentos

| Doc | Assunto |
|---|---|
| [`cloudflare-tunnel.md`](cloudflare-tunnel.md) | Expor o app via Cloudflare Tunnel (opção principal). |
| [`alternatives.md`](alternatives.md) | Alternativas (ngrok, Tailscale Funnel) e comparação. |

## Princípios

- **PC como servidor** (fase inicial, custo zero); migrar para hospedagem depois.
- Acesso por **link único** (PC e celular), com **HTTPS**.
- **Segurança:** não expor admin/DB publicamente; segredos protegidos (ver [`../security/`](../security/)).
- Usa as **portas não-padrão** ([`../unit/infra/ports.md`](../unit/infra/ports.md)).

## Regra de manutenção

Atualizar quando o método/endereço de distribuição mudar e registrar em [`CHANGELOG.md`](CHANGELOG.md).
