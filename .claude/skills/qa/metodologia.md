# Metodologia do harness de QA — agnóstica ao projeto

**Status:** vigente · **Motor:** ver `motor/VERSAO` · **Dono:** Micael

Este é o documento operacional da skill `/qa`. Vale igual em qualquer projeto:
o que muda de um projeto para outro é só **configuração** (`qa-harness/config.yaml`),
**adaptador** (`qa-harness/adaptador.py`) e **especificação** (`spec/`). Quando um
projeto precisa de algo diferente, isso vai para o `spec/qa/05-harness-metodologia.md`
dele — e esse documento do projeto manda sobre este só no que for específico.

---

## 1. Princípios

1. **Caixa-preta.** O harness testa a aplicação de fora (HTTP e navegador). Nunca
   importa código do produto, nunca edita o produto.
2. **Nenhuma alegação sem evidência.** "Passou" exige saída real de execução, com
   arquivo de prova em disco.
3. **200 não é prova.** Um ponto só é válido se a evidência *mostrar* o dado
   esperado. Status HTTP sozinho, tela que só abriu, jornada que só navegou — nada
   disso prova funcionalidade.
4. **Determinismo.** Histórias saem só da instrução de derivação; relatório e PDF
   saem só do manifesto; o motor não descobre telas nem inventa texto.
5. **Mocks só na fronteira externa.** A stack real é o ambiente de teste. O que
   depende de integração desligada vira `[limitação de ambiente]`, não falha.
6. **Nomenclatura sem abreviações:** `<PALAVRA CHAVE> <NÚMERO> - <TÍTULO>` —
   História 1 - ..., Ponto 2 - ..., Achado 3 - .... Proibido US-01, P2, H1.

---

## 2. Arquitetura

```
~/.claude/skills/qa/                 FONTE CANÔNICA (global da máquina)
├── SKILL.md                         orquestração do /qa
├── metodologia.md                   este documento
├── adotar.md                        como levar o harness a um projeto novo
├── sincronizar.py                   global → projeto · conferência · projeto → global
├── motor/                           código agnóstico (Python)
└── modelos/                         o que um projeto novo copia e preenche

<projeto>/
├── .claude/skills/qa/               espelho da skill (sem o motor) — versionado
├── qa-harness/
│   ├── motor/                       cópia instalada do motor — NUNCA editar à mão
│   ├── executar.py                  3 linhas: chama motor.executar.principal
│   ├── config.yaml                  URLs, perfis, viewports, caminhos, alvos
│   ├── adaptador.py                 autenticação, massa, verificações, suítes
│   ├── testes/api/                  suítes de integração do projeto
│   ├── evidencias/                  provas (imagens fora do git)
│   └── relatorios/<execução>/       relatório, manifesto, revisão, PDFs
└── spec/                            histórias, planos, jornadas, base visual, convenções
```

- **A skill global é a fonte.** Mudança no harness começa em `~/.claude/skills/qa/`
  e chega ao projeto por `sincronizar.py`. `qa-harness/motor/` e
  `.claude/skills/qa/` do projeto são instalação: se divergirem da fonte, a fonte vence.
- **Precedência de skill no Claude Code:** skill pessoal (`~/.claude/skills/`)
  vence a de projeto com o mesmo nome. Por isso só existe **uma** `/qa`, agnóstica;
  o espelho no projeto serve a quem clona sem ter a skill global (ele instala com
  `python .claude/skills/qa/sincronizar.py . --instalar-global`).
- **Projeto sem `qa-harness/motor/`** é um harness anterior ao motor (modo legado):
  a skill segue os comandos do `spec/qa/05-harness-metodologia.md` daquele projeto,
  aplicando as regras permanentes daqui. Adotar o motor é decisão do dono do projeto.

---

## 3. Interface `/qa <modo>`

| Modo | O que roda | Saídas |
|---|---|---|
| `completo` | bootstrap → massa → comentários (em paralelo) → integração → base visual (monitor) → jornadas (monitor) → linhas do projeto → lint → manifesto → catálogo → PDFs → **revisão de validade** → consolidar | `relatorio.md` + `manifesto.yaml` + `revisao.yaml` + PDFs por história |
| `integracao` | só as suítes de API | relatório + manifesto (sem PDF) |
| `visual` | base visual + jornadas, em monitor | relatório + manifesto + evidências (sem PDF) |
| `jornadas` | só as jornadas (filtra por domínio / id / viewport) | idem |
| `responsividade` | base visual nos viewports de responsividade (e jornadas, com `--com-jornadas`) — **única forma de evidência fora do monitor** | relatório com seção de responsividade (sem PDF) |
| `relatorios` | PDFs do manifesto mais recente (ou do indicado) | `relatorios/<execução>/pdf/` |
| `comentarios` | só o coletor + julgamento da IA | seção de warnings |
| `lint` | amarração história ↔ plano ↔ jornada ↔ evidência | lacunas no console |
| `<linha do projeto>` | linha extra declarada no config (unitários, fluxogramas...) | pontos no manifesto |

Comando único: `python qa-harness/executar.py <modo>` (ver `--help`). `completo`
**não** inclui responsividade — outros viewports custam ~2× e ficam sob demanda.

---

## 4. Bootstrap (obrigatório antes de qualquer suíte)

`python qa-harness/executar.py bootstrap` confere: dependências do motor e as
extras do projeto; `config.yaml` e adaptador carregáveis; Chromium do Playwright
(baixa/atualiza sozinho); aplicação respondendo **e sendo esta aplicação**
(`projeto.assinatura_da_aplicacao` precisa aparecer na home — outro projeto na
mesma porta produziria um relatório inteiro de mentira); verificações do projeto
(`Adaptador.verificar_ambiente`: banco, schema, contas); versão do motor contra a
global (aviso). Vermelho → reportar os impedimentos e parar.

---

## 5. Massa de dados

O adaptador recoloca o banco num **estado conhecido** antes de medir
(`Adaptador.preparar_massa`). Regras: escreve direto na persistência, sem passar
pelo código testado; tudo que cria tem prefixo reconhecível (`qa-`) e é apagado
antes de ser recriado (rodar duas vezes dá o mesmo banco); cada regra de negócio
tem o **contraste** que a prova (quem tem e quem não tem acesso, o item visível e
o oculto, um texto sentinela que nunca pode aparecer).

---

## 6. Cadeia de teste

```
spec vigente → história (spec/test/historias/<dominio>.md, via _instrucao.md)
            → plano (spec/test/planos/<dominio>.yaml)  → suíte de API (qa-harness/testes/api/)
            → jornada (spec/test/jornadas/<dominio>.yaml) → motor/jornadas.py
            → evidência → manifesto → revisão → relatório + PDF
```

### 6.1 Histórias

Derivadas **somente** pela `spec/test/historias/_instrucao.md` do projeto (modelo
em `modelos/`). Regras agnósticas da derivação:

- **Uma história é uma funcionalidade que alguém usa, do começo ao fim**: ator,
  ponto de entrada, resultado. Se não dá para dizer "começa quando ___ e termina
  quando ___", é detalhe de outra história.
- **Régua:** toda tela de painel e todo fluxo público aparece em pelo menos uma
  história.
- **Não vira história:** funcionalidade que não existe; tentar quebrar a página ou
  forçar erro sem valor de negócio; variação cosmética (outro viewport).
- **Recusa e permissão** (403, campo obrigatório, duplicado) são **critério de
  aceite dentro** da jornada a que pertencem, não história própria.
- Critério de aceite sempre cita a fonte; sem fonte não existe critério.
- Formato: cabeçalho com `**Derivado de:**` (fontes) e, se o domínio tem tela,
  `**Jornadas:** spec/test/jornadas/<dominio>.yaml`; cada história com
  `**Como** ..., **quero** ..., **para** ...`, `**Fontes:**` e `- [ ]` critérios.
  `**Prova visual:** não se aplica — <motivo>` dispensa a jornada de uma história
  (só quando ela não tem tela nenhuma).
- Histórias não se editam à mão: regenera-se o domínio pela instrução e versiona-se o diff.

### 6.2 Planos

```yaml
dominio: catalogo
fontes: [caminho/da/fonte]
historias: spec/test/historias/catalogo.md
pontos:
  - nome: "Ponto 1 - <título>"
    historia: "História 1 - <título exato>"
    suite: integracao                 # integracao | <linha do projeto>
    pre_condicoes: [estado de massa exigido]
    fluxo:
      - passo: "autenticar como X e GET /rota"
        evidencia: json               # json | png   (txt é proibido)
    validade: >
      o que a evidência precisa MOSTRAR para o ponto ser válido — não o status HTTP
    limitacoes_ambiente: []
```

A prova visual das histórias **não** fica no plano: é a jornada. O retrato tela a
tela é a base visual. Ponto de integração do plano sem teste, ou teste sem ponto no
plano, é lacuna reportada pelo lint.

### 6.3 Jornadas — prova visual obrigatória

Toda história que toca o frontend tem jornada declarativa: **um print por passo**,
primeiro passo marcado `INICIO`, último `FIM`, legenda (`titulo`) acima de cada
imagem no PDF. Contrato completo em `modelos/spec/test/jornadas/_contrato.yaml`.

```yaml
dominio: catalogo
historias: spec/test/historias/catalogo.md
jornadas:
  - id: assinante-ve-o-catalogo
    nome: Assinante vê o estado de cada título
    historia: "História 1 - <título exato>"
    ator: assinante
    entra_como: assinante                # perfil do config.yaml; visitante = sem sessão
    limpeza: {recurso: ..., prefixo: "QA "}   # opcional, executada pelo adaptador
    passos:
      - { acao: abrir, rota: "/app/catalog", titulo: "Abre o catálogo" }
      - { acao: conferir_texto, texto: "QA Filme", titulo: "Vê o título incluso" }
```

Vocabulário: `abrir {rota}` · `clicar {texto|seletor|aba}` ·
`preencher {campo|tipo|seletor, valor}` · `selecionar {campo|seletor, opcao|indice}` ·
`teclar {tecla[, campo|seletor]}` (Enter, Escape... — formulário sem botão) · `esperar {ms}` · `entrar_como {perfil[, rota]}` (troca a sessão no meio da jornada) ·
`conferir_texto {texto, dentro_de?}` · `conferir_ausencia {texto, dentro_de?}` ·
`conferir_url {termina_em|contem}` · `conferir_elemento {seletor}`.

Regras: toda jornada declara uma história existente; tem **pelo menos um passo de
conferência** (jornada que só navega não prova nada); tem pelo menos dois passos;
só funcionalidade que existe; o que ela cria usa `{{execucao}}` no nome (senão a
próxima execução enxerga o registro da anterior); texto conferido é o
**renderizado** (`innerText`, com `text-transform`), sem diferenciar caixa.

Veredito automático: conferência que não se confirma → FALHA DE PRODUTO; passo que
não executa (seletor ausente, navegação que estoura) → EVIDENCIA INVALIDA.

### 6.4 Base visual

Retrato do sistema tela a tela, **independente de história**, declarado em
`spec/test/planos/_base-visual.yaml` (perfil → telas por `rota` ou `aba`). É o que
revela quebra em tela que nenhuma jornada cobre, e é a linha de base da regressão
visual. Capturada em monitor; outros viewports só em `/qa responsividade`. Um ponto
por perfil e viewport: tela que não abre, que renderiza abaixo do mínimo de texto
ou que tem rolagem horizontal é problema. Tela curta por design declara
`texto_minimo` própria no catálogo. Antes de cada captura o motor rola a página até
o fim e volta, para a imagem com carregamento preguiçoso aparecer no print.

O limiar de texto não enxerga tudo: página "não encontrada" dentro do layout do
site passa do mínimo. A revisão da IA olha cada print — link do menu levando a 404
é falha de produto mesmo com o veredito automático VÁLIDO.

Medir cedo demais registra tela em branco ou a URL de antes de um redirecionamento
do lado do cliente. Toda navegação espera **URL estável e texto firme** antes de
medir (`execucao.tentativas_de_assentamento` × `intervalo_de_assentamento_ms`).

---

## 7. Evidências

```
qa-harness/evidencias/
├── _contrato.yaml
├── CHANGELOG-EVIDENCIAS.yaml                  linha do tempo por tela (versionado)
├── _base/<perfil>/<viewport>/                 <nome>.png + evidencias.json
├── jornadas/<dominio>/<jornada>/<viewport>/   <NN-passo>.png + evidencias.json
├── _olhar/<perfil-rota>/<viewport>/           print avulso de revisão (fora do manifesto)
└── api/<dominio>/<NN-acao>.json               request + response completos
```

- **Um `evidencias.json` por pasta de imagens**, chaveado pelo nome do `.png`: as
  métricas da captura (URL, marco, título, texto renderizado, `scrollWidth` ×
  `innerWidth`, o que foi observado) e **o PNG cru em base64**, com `sha256` e
  `bytes`. Métricas primeiro, base64 por último (o diff começa legível).
- **Tamanho da captura.** Passo de jornada = a **janela visível** (o que a pessoa vê),
  com o texto ou elemento conferido trazido à vista antes do print. Base visual =
  página inteira até `execucao.altura_maxima_da_captura_px` (padrão 4320). Página
  inteira em cada passo multiplica o peso versionado sem provar nada a mais.
- **O `.png` não vai ao git; o `evidencias.json` vai.** Base64 engorda 33% em texto,
  mas o git guarda o blob comprimido e o zlib recupera quase toda a folga — não há
  motivo para perder qualidade: evidência que não dá para ler não é evidência.
  Quem clona devolve as imagens com `python qa-harness/executar.py reverter`
  (confere o sha256); o PDF desfaz o base64 sozinho, sob demanda.
- **Nunca** um `.json` ao lado de cada print (formato antigo = erro de contrato).
- Reexecução reescreve a pasta inteira: tela renomeada não sobrevive.
- **Só `.png` e `.json`.** Dump de stdout (`.txt`) é proibido: não é parseável, não
  identifica o que provou e deixa vários pontos citarem o mesmo arquivo genérico.
- **Dois pontos não compartilham arquivo de evidência** — o motor recusa em execução.
- **Texto conferido em página grande vai declarado.** O `.json` de API guarda um
  recorte do corpo não-JSON, e recorte não prova presença nem ausência. A suíte
  passa `procurar=[...]` ao `_chamar` e a evidência grava
  `procurado_no_corpo_inteiro` (quantas vezes cada texto aparece no corpo inteiro).
  Ausência só vale com contraste: junto do texto que não pode aparecer, um que tem
  de aparecer (senão a ausência prova só página vazia).
- Nada de evidência editada ou recortada à mão.
- **Changelog por tela** (`CHANGELOG-EVIDENCIAS.yaml`): cada caminho de imagem é uma
  chave com as execuções dentro; miniatura (480px, JPEG q60) só quando o sha256
  muda, senão `identica_a`. O `git diff` mostra exatamente quais telas mudaram.
  O `evidencias.json` é a tela de agora, inteira; o changelog é a linha do tempo.
- Antes de propor commit: `python qa-harness/executar.py reverter --conferir`
  (0 = todo base64 bate com o `.png` em disco e nenhum `.png` está fora do JSON).

---

## 8. Revisão de validade e healing

O motor dá o **veredito automático**. A IA então **audita cada ponto** contra o
campo `validade` do plano (ou, na jornada, contra a história e os critérios):
lê os prints como imagem e os `.json` como dado.

| Veredito | Quando | Destino |
|---|---|---|
| **VÁLIDO** | a evidência prova o que o ponto alega | placar |
| **FALHA DE PRODUTO** | a evidência prova comportamento errado | ajuste/retorno para o desenvolvimento |
| **EVIDÊNCIA INVÁLIDA** | o teste não provou nada (200 vazio, seletor errado, tela medida cedo) | **healing**: corrige-se o TESTE, nunca o produto; reexecuta; revalida |
| **INCONCLUSIVO** | depois de 3 ciclos de healing sem prova | relatório — proibido fingir verde |

A decisão da IA vai para `qa-harness/relatorios/<execução>/revisao.yaml` (formato
no cabeçalho de `motor/manifesto.py`): vereditos alterados com motivo e ciclos de
healing, julgamento dos comentários, artefatos criados. Depois,
`python qa-harness/executar.py consolidar <execução>` aplica ao manifesto,
renderiza o relatório de novo e regenera os PDFs. Nenhuma seção do relatório é
escrita à mão.

Healing de jornada: `python qa-harness/executar.py jornadas <dominio> --jornada <id>`
reexecuta só ela; `olhar <rota> <perfil>` tira um print avulso para entender a tela.

---

## 9. Convenção de comentários — etapa de IA, em paralelo

Regra do projeto em `spec/code/convencao-de-comentarios.md` (modelo em `modelos/`):
**o código explica o que faz agora; a história de como chegou aqui mora no `.md`.**
Changelog, decisão, fluxo e achado de QA não vivem no código; comentário usa a
convenção da linguagem (Python → docstring; JS/TS → JSDoc para contrato, `//` curto).

1. **Paralela.** O coletor não usa banco, navegador nem container: o `completo` o
   dispara no início (`relatorios/<execução>/comentarios.json`) e a IA julga
   enquanto as suítes rodam.
2. **Julgada por IA.** O coletor entrega candidato (`narrativa` · `codigo-comentado`
   · `convencao` · `bloco-longo`), nunca veredito, e sai sempre com 0. Regex não
   separa data de negócio de data de changelog: data que registra *quando um número
   mágico foi medido* é o presente do teste, e se aceita.
3. **Sempre warning.** Comentário fora de lugar é dívida de documentação: não
   derruba a execução, não vira FALHA DE PRODUTO, não entra no healing nem no placar.
   Sai na seção "Warnings - Convenção de comentários" com arquivo, linha e para
   qual `.md` migrar, mais os aceitos com o porquê.

Correção de comentário no produto é ajuste/retorno para o desenvolvimento; no
`qa-harness/` (fora do `motor/`) o QA corrige sozinho; no motor, corrige-se na fonte global.

---

## 10. Relatórios

Cada execução cria `qa-harness/relatorios/<AAAA-MM-DD-HHMM>/`:

- `manifesto.yaml` — máquina: cada ponto com domínio, história, suíte, viewport,
  veredito (e o automático, se a revisão mudou), healing, caminho percorrido e
  evidências. **Única entrada** do relatório, do PDF e do catálogo.
- `relatorio.md` — humano, renderizado do manifesto: placar, integração, jornadas,
  base visual, responsividade, linhas do projeto, **ajuste/retorno** (achados),
  lacunas de especificação, revisão de validade e healing, **warnings de
  comentários**, **criados nesta execução**.
- `revisao.yaml` — a decisão da IA (seção 8).
- `comentarios.json` — candidatos do coletor (não é evidência: fica no relatório).
- `pdf/` — **um PDF por história** (só no `completo` e no `relatorios`): história e
  critérios da spec, verificações, leitura de cada evidência e o caminho percorrido
  tela a tela com a legenda de cada passo. Fica fora do git; regenera-se do manifesto.

### 10.1 Markdown seguro — nenhuma marcação crua no relatório

Texto livre entra no `relatorio.md` o tempo todo — leitura automática, motivo da
revisão, detalhe de falha, problema da base visual — e esse texto cita código e
HTML: `<td>`, `<a>`, `sql<number>`. Cru, o preview de markdown **interpreta a
tag**: ela some, a frase sai truncada e o achado fica ilegível exatamente onde
mais importa. Aconteceu na primeira execução do lia-scott-platform
(2026-09-26-1309): "`<td>` dentro de `<a>`, `<a>` dentro de `<tr>`" apareceu no
preview como uma frase sem as tags.

Duas camadas, as duas obrigatórias:

1. **O motor protege.** `motor/manifesto.py` passa **toda linha** do relatório por
   `proteger_markdown()`: qualquer marcação HTML fora de um trecho de código vai
   para dentro de crases. Células de tabela passam por `celula_de_tabela()`, que
   escapa a barra vertical. O gerador nunca escreve HTML de propósito — então toda
   tag numa linha veio de texto livre e tem de aparecer literal.
2. **Quem escreve o texto já escreve certo.** Ao redigir o `motivo` do
   `revisao.yaml`, uma leitura de teste ou um critério de validade, cite código,
   HTML, rota, seletor e nome de campo **entre crases**: `` `<td>` ``,
   `` `/api/super-admin/users` ``, `` `totalCents` ``. A proteção do motor é rede de
   segurança, não licença para escrever cru.

O PDF não tem esse problema (texto é texto no fpdf2); a regra é do markdown.

---

## 11. Linhas do projeto

Etapas que só um projeto tem (unitários in-tree, fluxogramas vivos...) entram por
`linhas_do_projeto` no `config.yaml`: um comando e um arquivo de resultado com
pontos no formato do manifesto. `no_completo: true` inclui a linha no `/qa completo`.
O motor só executa e consolida — a lógica é do projeto.

---

## 12. Contratos de pasta e criação autônoma

Cada pasta da cadeia tem `_contrato.yaml` legível por máquina (modelos em
`modelos/`): `spec/test/historias/`, `spec/test/planos/`, `spec/test/jornadas/`,
`qa-harness/testes/`, `qa-harness/evidencias/`.

Durante uma execução, o `/qa` **pode criar** artefato que falte — história, plano,
jornada, teste — só dentro destes limites:

1. **Gatilho objetivo:** lacuna detectada (tela sem história, história de frontend
   sem jornada, ponto de plano sem teste, achado confirmado sem regressão).
2. **Derivação determinística:** fonte vigente → história (`_instrucao.md`) → plano
   (schema + contrato) → teste ou jornada. Sem rastro a uma fonte, não se cria.
3. O que foi criado entra em `criados_nesta_execucao` do `revisao.yaml` (e daí no
   relatório) e na proposta de commit — **criação não é aprovação**.
4. **Proibido:** tocar o produto; reescrever teste ou jornada existente fora de
   healing; escrever Gherkin; editar `qa-harness/motor/` no projeto.
5. Na dúvida entre criar e reportar lacuna: **reportar**.

---

## 13. Placar e encerramento

**Placar em toda resposta do `/qa`**, numa caixa de código:

```
QA placar — <projeto> · <modo> · execução <carimbo>
EXECUTADO  (provado rodando, com evidência)
  integração  N/M válidos · jornadas N/M · base visual N/M perfis
  achados: N falha(s) de produto · healing: N ciclo(s) · inconclusivos: N
CONTADO    (estático, sem execução)
  histórias N · jornadas declaradas N · telas na base N · lacunas de spec N
TRABALHO   (o que esta resposta fez)
  ...
```

Encerramento de todo modo que executa: revisão de validade → `consolidar` →
`reverter --conferir` (se houve imagem) → atualizar o arquivo de status do projeto,
se ele declarar um (`projeto.arquivo_de_status`) → placar → **proposta de commit**:
blocos separados e copiáveis (`git add ...` e `git commit -m "..."`), aguardando o
OK. **Nunca commitar.** Sem linha `Co-Authored-By`.

Entra no commit: `evidencias.json` das pastas tocadas, `.json` de API,
`CHANGELOG-EVIDENCIAS.yaml`, `relatorio.md` + `manifesto.yaml` + `revisao.yaml` +
`comentarios.json` da execução, specs e testes criados, motor/espelho atualizados.
Fica fora (`.gitignore`): `*.png` e `*.pdf` do `qa-harness/`.

---

## 14. Regras permanentes (violação = trabalho inválido)

- Placar em toda resposta; EXECUTADO só com saída real.
- Nunca editar o produto (pastas em `projeto.produto_somente_leitura`); ler pode.
- Nunca editar `qa-harness/motor/` no projeto: muda-se a fonte global e sincroniza.
- Commits só propostos, em blocos separados, aguardando aprovação; sem `Co-Authored-By`.
- Nomenclatura sem abreviações.
- Histórias só pela instrução; PDFs só pelo manifesto; relatório só renderizado.
- Um `evidencias.json` por pasta de imagem; `.txt` proibido; evidência não compartilhada.
- Warning de comentário nunca vira reprovação.
- Atualizar no mesmo passo os `.md` afetados (spec do projeto e status).
