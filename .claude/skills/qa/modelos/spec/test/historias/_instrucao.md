# Instrução determinística — Derivação de Histórias de Usuário

**Status:** vigente · **Modelo:** skill `/qa` (`modelos/spec/test/historias/_instrucao.md`)
Quem deriva histórias (skill `/qa` ou qualquer agente) segue ESTE arquivo.
Mesma entrada ⇒ mesmas histórias. Nada é inventado fora das fontes.

## Entrada obrigatória (por domínio)

<!-- PREENCHER: as fontes de verdade DESTE projeto, em ordem de precedência.
     Ex.: 1. spec/planning/<dominio>.md vigente · 2. spec/bdd/<dominio>.feature ·
     3. as telas reais (arquivo de rotas do frontend) e as rotas reais (OpenAPI) ·
     4. o schema do banco. Sem planejamento no projeto, o código implementado é a
     fonte primária e normativa. -->

Sem fonte **e** sem tela/rota correspondente, não há história: reporte lacuna.

## O que é uma história (granularidade)

Uma história é **uma funcionalidade que alguém usa, do começo ao fim**: tem um
ator, um ponto de entrada e um resultado obtido. Se não dá para dizer "começa
quando ela ___ e termina quando ela ___", não é uma história — é detalhe de outra.

**Régua prática:** toda tela de painel e todo fluxo público aparece em pelo menos
uma história. Painel com dez telas e domínio com duas histórias = derivação grossa demais.

### O que NÃO vira história
- Funcionalidade que **não existe** no produto — não se inventa jornada para criar expectativa.
- Tentar **quebrar** a página, forçar erro sem valor de negócio, entrada absurda.
- **Recusa e permissão** (403, campo obrigatório, duplicado) — viram *critério de
  aceite dentro* da jornada a que pertencem, nunca história própria.
- Variação cosmética da mesma jornada (a mesma tela em outro viewport).

## Regras de derivação

1. Uma história por funcionalidade, na ordem em que a pessoa a encontra no produto
   (entrada → uso → resultado).
2. Nomeação: `História <número> - <assunto>` — assunto em até 8 palavras, sem
   abreviações, do ponto de vista de quem usa.
3. Papel real do sistema. <!-- PREENCHER: os papéis deste projeto e onde cada um é definido. -->
4. Critérios de aceite **somente** das fontes, citando a fonte de cada um. Proibido inventar critério.
5. Comportamento coberto por mock ou integração desligada → critério marcado
   `[limitação de ambiente]`, nunca falha de produto.

## Prova visual é obrigatória para quem tem tela

Toda história cujo ator é uma pessoa e cujo domínio tem tela precisa de ao menos
uma jornada em `spec/test/jornadas/<dominio>.yaml` (contrato em `_contrato.yaml`
daquela pasta): um passo por ação, cada um com print (primeiro `INICIO`, último
`FIM`), pelo menos um passo de conferência provando o resultado, e dados próprios
por execução (`{{execucao}}`) quando cria registro.

História de frontend sem jornada é **lacuna** e o `/qa` a reporta. História sem
tela nenhuma declara `**Prova visual:** não se aplica — <motivo>`.

## Formato fixo de saída (`spec/test/historias/<dominio>.md`)

```markdown
# Histórias de Usuário — <Domínio>

**Status:** vigente · **Derivado de:** <fontes> · **Instrução:** `_instrucao.md`
**Jornadas:** `spec/test/jornadas/<dominio>.yaml`   ← quando o domínio tem tela

## História 1 - <assunto>
**Como** <papel>, **quero** <ação>, **para** <valor>.
**Fontes:** <arquivo>:<seção ou símbolo> · <tela ou rota real>
**Critérios de aceite:**
- [ ] <critério> (fonte: <arquivo>)
- [ ] <critério> [limitação de ambiente] (fonte: <arquivo>)
```

## Regeneração

Fontes ou telas mudaram, ou esta instrução mudou → regenerar o domínio inteiro por
ela e versionar o diff. Histórias não se editam à mão fora da regeneração.
Renomear história obriga a atualizar, no mesmo passo, planos, jornadas e testes que a citam.
