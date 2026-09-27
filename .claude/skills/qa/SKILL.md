---
name: qa
description: Harness de QA agnóstico ao projeto (black-box) - bootstrap do ambiente, massa de dados, suítes de integração HTTP, base visual e jornadas de usuário com Playwright (um print por passo, INICIO e FIM), evidência em evidencias.json com PNG em base64, revisão de validade com healing, convenção de comentários julgada por IA, relatório .md/.yaml e PDF por história. Use quando o usuário digitar /qa completo, /qa integracao, /qa visual, /qa jornadas, /qa responsividade, /qa relatorios, /qa comentarios, /qa lint ou /qa <linha do projeto>, em qualquer projeto que tenha qa-harness/.
---

# Skill /qa — harness de QA agnóstico

Fonte canônica: `~/.claude/skills/qa/` (esta pasta). O documento operacional é
`metodologia.md` desta pasta — **leia-o antes de executar**; ele manda sobre este
arquivo. O que for específico do projeto está no `spec/qa/05-harness-metodologia.md`
dele, que manda sobre a metodologia só no que for específico.

Caminhos desta skill: `SKILL_QA = ~/.claude/skills/qa` (Windows:
`C:\Users\<usuario>\.claude\skills\qa`).

## Passo 0 — Pré-checagens (sempre, em qualquer modo)

1. **Qual projeto é.** Existe `qa-harness/` na raiz? Se não existe, informe que o
   projeto ainda não tem harness e aponte `adotar.md` — não crie nada sem pedido.
2. **Motor ou legado.**
   - Existe `qa-harness/motor/`: rode
     `python "$SKILL_QA/sincronizar.py" . --conferir`.
     Divergência com motor global igual ou mais novo → rode
     `python "$SKILL_QA/sincronizar.py" .` e liste os arquivos atualizados na
     proposta de commit. Motor do projeto **mais novo** que o global → pare e
     pergunte ao usuário (alguém evoluiu o harness em outra máquina).
   - Não existe `qa-harness/motor/`: **modo legado**. Siga os comandos do
     `spec/qa/05-harness-metodologia.md` do projeto, aplicando as regras
     permanentes abaixo, e registre "adotar o motor agnóstico" como pendência.
3. Leia `metodologia.md` (esta pasta) e o `spec/qa/05-harness-metodologia.md` do projeto.
4. `python qa-harness/executar.py bootstrap`. Vermelho → reporte os impedimentos
   e pare. Subir o ambiente local (banco, servidor de desenvolvimento) é permitido
   quando o `05` do projeto disser como; depois, bootstrap de novo.

## Regras permanentes (violação = trabalho inválido)

- **Placar em toda resposta** (formato na seção 13 da metodologia): EXECUTADO só
  com saída real e evidência · CONTADO · TRABALHO.
- **Nenhuma alegação sem evidência.** 200 não é prova; jornada que só navega não é prova.
- **Nunca editar o produto** (`projeto.produto_somente_leitura` do `config.yaml`).
  Correção de produto é ajuste/retorno para o desenvolvimento.
- **Nunca editar `qa-harness/motor/`** num projeto: muda-se a fonte global e sincroniza.
- **Commits só propostos**: um bloco copiável com `git add ...`, outro com
  `git commit -m "..."`, aguardando o OK. Nunca commitar. Sem linha `Co-Authored-By`.
- **Nomenclatura sem abreviações**: `<PALAVRA CHAVE> <NÚMERO> - <TÍTULO>`.
- **Determinismo**: histórias só por `spec/test/historias/_instrucao.md`; relatório
  e PDF só do `manifesto.yaml`; decisões da IA só por `revisao.yaml` + `consolidar`.
- **Evidência**: um `evidencias.json` por pasta de imagem (PNG cru em base64); nunca
  `.json` ao lado de cada print; `.txt` proibido; dois pontos não dividem arquivo.
- **Warning de comentário nunca vira reprovação.**
- **Markdown seguro.** Em todo texto que vai para o relatório (`motivo` da revisão,
  leitura, critério), código, HTML, rota, seletor e campo vão **entre crases**. O
  motor ainda protege toda linha (`proteger_markdown`), mas marcação crua como
  `<td>` ou `sql<number>` some no preview — metodologia, seção 10.1.
- Atualizar no mesmo passo os `.md` afetados (spec do projeto; status, se declarado).

## Dispatch por parâmetro

Todos rodam `python qa-harness/executar.py <modo>` na raiz do projeto.

### `/qa completo`
1. **Análise → plano.** Leia as fontes vigentes do(s) domínio(s) e confira a cadeia
   com `python qa-harness/executar.py lint`. Lacuna objetiva → criação autônoma
   (seção 12 da metodologia) ou reporte.
2. **Execução.** `python qa-harness/executar.py completo` — rode em segundo plano:
   leva minutos. Ele dispara o coletor de comentários em paralelo e grava
   `qa-harness/relatorios/<execução>/comentarios.json` logo no início.
3. **Comentários, enquanto as suítes rodam.** Assim que o `comentarios.json`
   aparecer, julgue cada candidato (tabela abaixo) e já vá montando a seção
   `comentarios:` do `revisao.yaml`.
4. **Revisão de validade.** Com o manifesto pronto, audite **cada ponto**: prints
   como imagem (abra os `.png` das jornadas e da base), `.json` como dado, contra o
   `validade` do plano ou os critérios da história. Divergiu do automático →
   registre no `revisao.yaml` com o motivo.
5. **Healing** de EVIDÊNCIA INVÁLIDA: corrija o teste ou a jornada (nunca o
   produto), reexecute só o necessário (`jornadas <dominio> --jornada <id>`,
   `integracao`), revalide. Máximo 3 ciclos por ponto; depois, INCONCLUSIVO.
   Registre `ciclos_de_healing` e o motivo no `revisao.yaml`.
6. **Consolidar.** `python qa-harness/executar.py consolidar <execução>` — aplica
   a revisão, renderiza `relatorio.md` e regenera os PDFs.
7. **Encerramento** (abaixo).

Não inclui responsividade.

### `/qa integracao` · `/qa visual` · `/qa jornadas [dominio] [--jornada id]`
Rodam só a linha pedida (visual = base visual + jornadas em monitor), sem PDF.
Revisão de validade, healing e `consolidar` iguais ao completo.

### `/qa responsividade`
`python qa-harness/executar.py responsividade [--com-jornadas]` — única forma de
evidência fora do monitor. Foco da revisão: quebra de layout, rolagem horizontal,
elemento inacessível; sai na seção de responsividade para o desenvolvimento. Sem PDF.

### `/qa relatorios`
`python qa-harness/executar.py relatorios [execução]` — um PDF por história a
partir do manifesto mais recente (ou do indicado). Sem manifesto: informe que é
preciso executar uma suíte antes. Sem manifesto não há PDF.

### `/qa comentarios`
`python qa-harness/executar.py comentarios --execucao <execução>` (ou `--json` para
só imprimir). Julgue cada candidato contra `spec/code/convencao-de-comentarios.md`:

| Veredito | Quando | Relatório |
|---|---|---|
| `violacao` | conta história (changelog, decisão, achado, healing), é código morto ou fere a convenção da linguagem | warning com arquivo, linha, categoria, o quê e destino (`.md` para onde migrar) |
| `aceitavel` | explica o presente, é restrição externa ou ponteiro curto para um `.md` | lista de aceitos, com o porquê |

Data que registra *quando um número foi medido* é o presente do teste: aceite.
Sempre warning — nunca derruba a execução nem entra no healing.

### `/qa lint`
`python qa-harness/executar.py lint` — história ↔ plano ↔ jornada ↔ evidência.
Cada achado é lacuna de especificação: crie (seção 12) ou reporte.

### `/qa <linha do projeto>`
Linhas declaradas em `linhas_do_projeto` do `config.yaml` (unitários, fluxogramas…):
`python qa-harness/executar.py linha <nome>`.

## Encerramento (todo modo que executa)

1. `revisao.yaml` escrito e `consolidar` rodado — sem revisão, o relatório diz
   "revisão pendente" e o trabalho não terminou.
2. Se houve imagem: `python qa-harness/executar.py reverter --conferir` (0 = íntegro).
3. Arquivo de status do projeto, se `projeto.arquivo_de_status` existir.
4. Placar final na resposta.
5. Achados (FALHA DE PRODUTO) e lacunas resumidos, cada um rastreável até a evidência.
6. Proposta de commit em blocos copiáveis, aguardando o OK.
