# .spec/security/

Trilha **viva** de segurança em nível de sistema: **modelo de ameaças** (threat model)
que consolida os controles espalhados nas units de [`../unit/security/`](../unit/security/)
e no planning [`19`](../planning/19-seguranca-e-lgpd.md)/[`20`](../planning/20-entrega-ebook-anti-pirataria.md).

> Diferença: `unit/security/` = *como* implementar cada controle (testável);
> `security/` (aqui) = *quais ameaças* existem e *como* os controles as mitigam.

## Documentos

| Doc | Assunto |
|---|---|
| [`threat-model.md`](threat-model.md) | Ativos, superfícies, ameaças (STRIDE) e mitigações. |

## Regra de manutenção

Revisar o threat model a cada novo domínio/superfície (ex.: ao gerar units da visão
completa) e registrar em [`CHANGELOG.md`](CHANGELOG.md).
