# 20 — Entrega de E-book e Anti-Pirataria

> Documento de planning · e_seller · 2026-06-06
> Como entregar o arquivo **só a quem pagou** e dificultar o vazamento.

---

## 1. Princípio

O arquivo do e-book é o produto. Ele **nunca** pode ser acessível por URL pública
direta e só é liberado após pagamento confirmado (RNF-01, RNF-03).

## 2. Armazenamento protegido

- Arquivos ficam em volume **separado** (`ebook_files`), **fora** do diretório de
  media público — o servidor web **não** os serve diretamente.
- O download passa **sempre** por uma view que valida permissão e faz *streaming*
  do arquivo (RF-33).

```
❌ /media/ebooks/livro.pdf        (jamais acessível direto)
✅ /download/<token>/             (view valida e transmite)
```

## 3. Link de download seguro (DownloadGrant)

Emitido quando o pedido vira `paid`:
- `token`: aleatório, longo, gerado por gerador **criptograficamente seguro** (`secrets`).
- `expires_at`: validade (sugestão: 7 dias).
- `max_downloads`: limite (sugestão: 5).
- `download_count`: incrementa a cada download bem-sucedido.

**Validação no download:**
```gherkin
Dado um token de download
Quando o cliente acessa /download/<token>/
Então liberar SOMENTE se:
  - o token existe
  - não está expirado (now < expires_at)
  - download_count < max_downloads
Senão retornar erro (inválido/expirado/limite)
```

## 4. Medidas anti-pirataria (proporcionais)

| Medida | Efeito | MVP? |
|---|---|---|
| Token único + expiração + limite | Reduz compartilhamento do link | ✅ |
| Arquivo nunca público | Impede hotlink direto | ✅ |
| **Marca d'água personalizada** (e-mail/pedido no PDF) | Desincentiva repasse (rastreável) | 🔶 Should |
| Watermark por página | Mais robusto | Could |
| DRM forte (criptografia/leitor próprio) | Alta proteção, alta complexidade/atrito | ❌ Won't (MVP) |

> 💡 **Realismo:** nenhum método impede 100% a cópia de um arquivo digital. A
> estratégia é **rastreabilidade + atrito**: marca d'água com o e-mail do comprador
> torna o vazamento identificável, o que costuma ser dissuasão suficiente.

## 5. Entrega ao cliente

- **MVP:** após o pagamento, a página de status do pedido exibe o link/botão de download.
- **Should:** e-mail transacional com o link (RF-32) — fora do MVP estrito.

## 6. Reemissão

- Cliente que perdeu o acesso (dentro da validade) pode solicitar reemissão do grant
  pela referência do pedido — gera novo token, respeitando regras.

## 7. Testes (resumo)

- Download válido transmite o arquivo e incrementa contador.
- Token expirado/limite atingido → negado.
- Path físico do arquivo não é acessível publicamente.
- Pedido não `paid` não possui grant.

## 8. Pendências

- [ ] Confirmar `expires_at` e `max_downloads` padrão.
- [ ] Incluir marca d'água no MVP+ (depende de lib gratuita de manipulação de PDF).
- [ ] Formatos suportados (PDF, EPUB) e validação por formato.
