"""Manifesto da execução, revisão de validade e `relatorio.md`.

O `manifesto.yaml` é a única entrada do relatório, do PDF e do catálogo de
evidências. O que a IA decide ao auditar as evidências (veredito revisado,
healing, julgamento dos comentários, artefatos criados) entra por um arquivo de
dados — `revisao.yaml`, na pasta da execução — e `consolidar` o aplica ao
manifesto e renderiza o relatório de novo. Nenhuma seção é redigida à mão.

Formato do `revisao.yaml`:
    auditoria: {pontos_auditados: 42, observacao: "..."}
    pontos:
      - {dominio: catalogo, nome: "Ponto 1 - ...", veredito: VALIDO,
         motivo: "...", ciclos_de_healing: 1}
    comentarios:
      - {arquivo: src/x.ts, linha: 10, veredito: violacao, categoria: narrativa,
         o_que: "changelog no código", destino: "spec/..."}
      - {arquivo: src/y.ts, linha: 3, veredito: aceitavel, porque: "..."}
    criados_nesta_execucao:
      - {caminho: spec/test/jornadas/x.yaml, o_que: "...", derivado_de: "..."}
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

import re

import yaml

from .evidencia import VEREDITOS

ORDEM_DAS_SUITES = ["integracao", "jornada", "base"]


def versao_do_motor() -> str:
    caminho = Path(__file__).resolve().parent / "VERSAO"
    if not caminho.exists():
        return "?"
    return caminho.read_text(encoding="utf-8").strip()


def pasta_mais_recente(config, exigir_manifesto: bool = True):
    """Pasta da execução mais recente em `relatorios/` (ou `None`)."""
    raiz = config.caminho("relatorios")
    if not raiz.exists():
        return None
    candidatas = []
    for item in sorted(raiz.iterdir()):
        if not item.is_dir():
            continue
        if exigir_manifesto and not (item / "manifesto.yaml").exists():
            continue
        candidatas.append(item)
    if not candidatas:
        return None
    return candidatas[-1]


def resolver_pasta_de_execucao(config, argumento: str = ""):
    """Aceita carimbo, pasta ou caminho do manifesto; vazio = mais recente."""
    if not argumento:
        return pasta_mais_recente(config)
    caminho = Path(argumento)
    if caminho.name == "manifesto.yaml":
        return caminho.parent.resolve()
    if caminho.is_dir():
        return caminho.resolve()
    candidata = config.caminho("relatorios") / argumento
    if candidata.is_dir():
        return candidata
    return None


def contar_placar(pontos: list) -> dict:
    placar = {}
    for veredito in VEREDITOS:
        placar[veredito] = 0
    for ponto in pontos:
        veredito = ponto.get("veredito", "INCONCLUSIVO")
        placar[veredito] = placar.get(veredito, 0) + 1
    return placar


# Marcacao que o preview de markdown interpretaria como HTML: <td>, </a>,
# <number> (como em sql<number>), <div class="x">. Texto livre do relatorio —
# leitura automatica, motivo da revisao, detalhe, nome de problema — cita codigo
# e HTML o tempo todo; cru, o preview engole a tag e a frase sai truncada ou com
# pedacos sumidos. Foi o que aconteceu na execucao 2026-09-26-1309: "<td> dentro
# de <a>, <a> dentro de <tr>" virou uma frase sem as tags.
MARCACAO_HTML = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?>")


def _em_crase(encontrado) -> str:
    return "`" + encontrado.group(0) + "`"


def proteger_markdown(linha: str) -> str:
    """Poe entre crases toda marcacao HTML que esteja FORA de um trecho de codigo.

    O gerador nunca escreve HTML de proposito, entao qualquer tag numa linha veio
    de texto livre e precisa aparecer literal. Trechos que ja estao entre crases
    ficam como estao — a divisao por crase alterna fora/dentro de codigo.
    """
    partes = str(linha).split("`")
    indice = 0
    while indice < len(partes):
        partes[indice] = MARCACAO_HTML.sub(_em_crase, partes[indice])
        indice = indice + 2
    return "`".join(partes)


def celula_de_tabela(texto) -> str:
    """Texto seguro dentro de uma celula: barra vertical fecharia a coluna."""
    return " ".join(str(texto or "").split()).replace("|", "\\|")


class Execucao:
    """Acumula os pontos de uma execução e grava manifesto e relatório."""

    def __init__(self, config, modo: str, viewports: list) -> None:
        self._config = config
        self._modo = modo
        self._viewports = viewports
        self._carimbo = datetime.now().strftime("%Y-%m-%d-%H%M")
        self._pasta = config.caminho("relatorios") / self._carimbo
        self._pontos: list = []
        self._lint: list = []
        self._linhas: dict = {}
        self._comentarios: dict = {}
        self._impedimentos: list = []

    @property
    def carimbo(self) -> str:
        return self._carimbo

    @property
    def pasta(self) -> Path:
        return self._pasta

    @property
    def pontos(self) -> list:
        return self._pontos

    def preparar_pasta(self) -> None:
        self._pasta.mkdir(parents=True, exist_ok=True)

    def adicionar(self, pontos: list) -> None:
        for ponto in pontos:
            self._pontos.append(ponto)

    def anotar_lint(self, achados: list) -> None:
        self._lint = list(achados)

    def anotar_linha(self, nome: str, informacao: dict) -> None:
        self._linhas[nome] = informacao

    def anotar_comentarios(self, resumo: dict) -> None:
        self._comentarios = resumo

    def anotar_impedimento(self, texto: str) -> None:
        self._impedimentos.append(texto)

    def gravar(self) -> Path:
        """Grava `manifesto.yaml` e renderiza `relatorio.md`."""
        self.preparar_pasta()
        serializados = []
        for ponto in self._ordenados():
            serializados.append(ponto.para_manifesto())
        manifesto = {
            "execucao": self._carimbo,
            "executado_em": datetime.now().isoformat(timespec="seconds"),
            "modo": self._modo,
            "projeto": self._config.nome_do_projeto,
            "branch": self._git(["branch", "--show-current"]),
            "commit": self._git(["rev-parse", "--short", "HEAD"]),
            "url_da_aplicacao": self._config.url_app,
            "motor": versao_do_motor(),
            "viewports": list(self._viewports),
            "placar": contar_placar(serializados),
            "lint_historias": self._lint,
            "linhas_do_projeto": self._linhas,
            "comentarios": self._comentarios,
            "impedimentos": self._impedimentos,
            "pontos": serializados,
        }
        caminho = self._pasta / "manifesto.yaml"
        gravar_yaml(caminho, manifesto)
        RelatorioMarkdown(self._config, manifesto, self._pasta).gravar()
        return caminho

    def _ordenados(self) -> list:
        def chave(ponto):
            suite = ponto.suite
            posicao = len(ORDEM_DAS_SUITES)
            if suite in ORDEM_DAS_SUITES:
                posicao = ORDEM_DAS_SUITES.index(suite)
            return (posicao, ponto.dominio)

        return sorted(self._pontos, key=chave)

    def _git(self, argumentos: list) -> str:
        try:
            resultado = subprocess.run(
                ["git"] + argumentos,
                cwd=str(self._config.raiz_projeto),
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            return "?"
        return resultado.stdout.strip() or "?"


class Consolidador:
    """Aplica o `revisao.yaml` da IA ao manifesto e renderiza o relatório."""

    def __init__(self, config, pasta: Path) -> None:
        self._config = config
        self._pasta = pasta

    def executar(self) -> dict:
        manifesto = carregar_yaml(self._pasta / "manifesto.yaml")
        caminho_revisao = self._pasta / "revisao.yaml"
        revisao = {}
        if caminho_revisao.exists():
            revisao = carregar_yaml(caminho_revisao) or {}
        alterados, nao_encontrados = self._aplicar_pontos(manifesto, revisao.get("pontos") or [])
        manifesto["placar"] = contar_placar(manifesto.get("pontos") or [])
        manifesto["revisao"] = {
            "arquivo": self._config.relativo(caminho_revisao) if caminho_revisao.exists() else "",
            "auditoria": revisao.get("auditoria") or {},
            "vereditos_alterados": alterados,
            "pontos_nao_encontrados": nao_encontrados,
            "comentarios": revisao.get("comentarios") or [],
            "criados_nesta_execucao": revisao.get("criados_nesta_execucao") or [],
        }
        gravar_yaml(self._pasta / "manifesto.yaml", manifesto)
        RelatorioMarkdown(self._config, manifesto, self._pasta).gravar()
        return manifesto

    def _aplicar_pontos(self, manifesto: dict, revisados: list):
        alterados = 0
        nao_encontrados = []
        for revisado in revisados:
            alvo = self._achar(manifesto.get("pontos") or [], revisado)
            if alvo is None:
                nao_encontrados.append(str(revisado.get("nome", "?")))
                continue
            veredito = str(revisado.get("veredito") or alvo.get("veredito"))
            if veredito not in VEREDITOS:
                raise ValueError("veredito inválido no revisao.yaml: " + veredito)
            if "veredito_automatico" not in alvo:
                alvo["veredito_automatico"] = alvo.get("veredito")
            if veredito != alvo["veredito_automatico"]:
                alterados = alterados + 1
            alvo["veredito"] = veredito
            if revisado.get("motivo"):
                alvo["revisao_motivo"] = str(revisado["motivo"]).strip()
            ciclos = int(revisado.get("ciclos_de_healing") or 0)
            if ciclos > int(alvo.get("ciclos_de_healing") or 0):
                alvo["ciclos_de_healing"] = ciclos
        return alterados, nao_encontrados

    def _achar(self, pontos: list, revisado: dict):
        nome = " ".join(str(revisado.get("nome", "")).split()).lower()
        dominio = str(revisado.get("dominio", ""))
        for ponto in pontos:
            mesmo_nome = " ".join(str(ponto.get("nome", "")).split()).lower() == nome
            if not mesmo_nome:
                continue
            if dominio and ponto.get("dominio") != dominio:
                continue
            return ponto
        return None


class RelatorioMarkdown:
    """Renderiza o `relatorio.md` a partir do manifesto (e da revisão, se houver)."""

    def __init__(self, config, manifesto: dict, pasta: Path) -> None:
        self._config = config
        self._m = manifesto
        self._pasta = pasta
        self._linhas: list = []

    def gravar(self) -> Path:
        self._cabecalho()
        self._placar()
        self._integracao()
        self._jornadas()
        self._base_visual()
        self._responsividade()
        self._linhas_do_projeto()
        self._ajuste_retorno()
        self._lacunas_de_especificacao()
        self._revisao_de_validade()
        self._warnings_de_comentarios()
        self._criados()
        destino = self._pasta / "relatorio.md"
        destino.write_text("\n".join(self._linhas) + "\n", encoding="utf-8")
        return destino

    # ── blocos ───────────────────────────────────────────────────────────

    def _escrever(self, *linhas) -> None:
        # Toda linha passa pela protecao: nenhum campo de texto livre chega cru ao
        # markdown, inclusive os que nao passam por _uma_linha (nome, historia).
        for linha in linhas:
            self._linhas.append(proteger_markdown(linha))

    def _cabecalho(self) -> None:
        m = self._m
        self._escrever(
            "# Relatório de QA — " + str(m.get("projeto", "")),
            "",
            "**Execução:** " + str(m.get("execucao"))
            + " · **Modo:** " + str(m.get("modo"))
            + " · **Viewports:** " + ", ".join(m.get("viewports") or [])
            + " · **Branch:** " + str(m.get("branch"))
            + " · **Commit:** " + str(m.get("commit"))
            + " · **Motor:** " + str(m.get("motor")),
            "",
            "Gerado de `manifesto.yaml` pelo motor da skill `/qa`. Evidência de imagem:"
            " `evidencias.json` de cada pasta (PNG em base64; `python qa-harness/executar.py"
            " reverter` devolve os arquivos).",
            "",
        )
        if m.get("impedimentos"):
            self._escrever("## Impedimentos", "")
            for impedimento in m["impedimentos"]:
                self._escrever("- " + str(impedimento))
            self._escrever("")

    def _placar(self) -> None:
        placar = self._m.get("placar") or {}
        pontos = self._m.get("pontos") or []
        self._escrever("## Placar", "", "| Veredito | Pontos |", "|---|---|")
        for veredito in VEREDITOS:
            self._escrever("| " + veredito + " | " + str(placar.get(veredito, 0)) + " |")
        ciclos = 0
        com_healing = 0
        for ponto in pontos:
            if int(ponto.get("ciclos_de_healing") or 0) > 0:
                com_healing = com_healing + 1
                ciclos = ciclos + int(ponto["ciclos_de_healing"])
        self._escrever("", "Healing: " + str(ciclos) + " ciclo(s) em " + str(com_healing) + " ponto(s).")
        revisao = self._m.get("revisao")
        if revisao:
            auditoria = revisao.get("auditoria") or {}
            self._escrever(
                "Revisão de validade: " + str(auditoria.get("pontos_auditados", "?"))
                + " ponto(s) auditado(s), " + str(revisao.get("vereditos_alterados", 0))
                + " veredito(s) alterado(s) em relação ao automático."
            )
        else:
            self._escrever(
                "Revisão de validade: **pendente** — vereditos abaixo são os automáticos do motor."
            )
        self._escrever("")

    def _por_suite(self, suite: str) -> list:
        encontrados = []
        for ponto in self._m.get("pontos") or []:
            if ponto.get("suite") == suite:
                encontrados.append(ponto)
        return encontrados

    def _integracao(self) -> None:
        pontos = self._por_suite("integracao")
        if not pontos:
            return
        self._escrever("## Integração", "")
        dominio_atual = None
        for ponto in pontos:
            if ponto.get("dominio") != dominio_atual:
                dominio_atual = ponto.get("dominio")
                self._escrever("### Domínio " + str(dominio_atual), "")
            self._escrever(
                "- **" + str(ponto["nome"]) + "** — " + self._selo(ponto),
                "  - História: " + str(ponto.get("historia", "")),
                "  - Leitura: " + self._uma_linha(ponto.get("detalhe", "")),
            )
            if ponto.get("revisao_motivo"):
                self._escrever("  - Revisão: " + self._uma_linha(ponto["revisao_motivo"]))
            evidencias = ponto.get("evidencias") or []
            if evidencias:
                self._escrever("  - Evidências: " + ", ".join(self._crases(evidencias)))
        self._escrever("")

    def _jornadas(self) -> None:
        pontos = self._por_suite("jornada")
        if not pontos:
            return
        self._escrever(
            "## Jornadas (prova visual das histórias)",
            "",
            "| Jornada | História | Viewport | Passos | Veredito |",
            "|---|---|---|---|---|",
        )
        for ponto in pontos:
            passos = str(ponto.get("passos_executados", "?")) + "/" + str(ponto.get("passos_declarados", "?"))
            self._escrever(
                "| " + celula_de_tabela(str(ponto["nome"]).replace("Jornada - ", ""))
                + " | " + celula_de_tabela(ponto.get("historia", ""))
                + " | " + str(ponto.get("viewport", ""))
                + " | " + passos
                + " | " + self._selo(ponto) + " |"
            )
        self._escrever("")
        for ponto in pontos:
            if ponto.get("veredito") == "VALIDO" and not ponto.get("revisao_motivo"):
                continue
            self._escrever("- **" + str(ponto["nome"]) + "**: " + self._uma_linha(ponto.get("detalhe", "")))
            if ponto.get("revisao_motivo"):
                self._escrever("  - Revisão: " + self._uma_linha(ponto["revisao_motivo"]))
        self._escrever("")

    def _base_visual(self) -> None:
        pontos = self._por_suite("base")
        if not pontos:
            return
        self._escrever(
            "## Base visual (retrato do sistema)",
            "",
            "| Perfil | Viewport | Telas | Erros de console | Veredito |",
            "|---|---|---|---|---|",
        )
        for ponto in pontos:
            perfil = str(ponto.get("historia", "")).replace("Base visual - ", "")
            self._escrever(
                "| " + perfil
                + " | " + str(ponto.get("viewport", ""))
                + " | " + str(len(ponto.get("percurso") or []))
                + " | " + str(len(ponto.get("erros_de_console") or []))
                + " | " + self._selo(ponto) + " |"
            )
        self._escrever("")
        for ponto in pontos:
            problemas = ponto.get("problemas") or []
            if problemas:
                self._escrever("- **" + str(ponto["nome"]) + "**: " + self._uma_linha("; ".join(problemas)))
        self._escrever("")

    def _responsividade(self) -> None:
        viewports = self._m.get("viewports") or []
        fora_do_monitor = []
        for viewport in viewports:
            if viewport != "monitor":
                fora_do_monitor.append(viewport)
        if not fora_do_monitor:
            return
        self._escrever("## Responsividade", "", "Viewports: " + ", ".join(fora_do_monitor) + ".", "")
        encontrou = False
        for ponto in self._m.get("pontos") or []:
            if ponto.get("viewport") not in fora_do_monitor:
                continue
            for problema in ponto.get("problemas") or []:
                if "rolagem horizontal" in problema or "falhou" in problema or "renderizou só" in problema:
                    self._escrever("- " + str(ponto["nome"]) + ": " + problema)
                    encontrou = True
        if not encontrou:
            self._escrever("Nenhuma quebra de layout, rolagem horizontal ou tela vazia nos viewports medidos.")
        self._escrever("")

    def _linhas_do_projeto(self) -> None:
        linhas = self._m.get("linhas_do_projeto") or {}
        if not linhas:
            return
        self._escrever("## Linhas do projeto", "")
        for nome in linhas:
            informacao = linhas[nome] or {}
            self._escrever(
                "- **" + nome + "**: saída " + str(informacao.get("codigo_de_saida"))
                + ", " + str(informacao.get("pontos", 0)) + " ponto(s). "
                + str(informacao.get("observacao", ""))
            )
        self._escrever("")

    def _ajuste_retorno(self) -> None:
        self._escrever("## Ajuste/retorno para o desenvolvimento", "")
        numero = 0
        for ponto in self._m.get("pontos") or []:
            if ponto.get("veredito") != "FALHA DE PRODUTO":
                continue
            numero = numero + 1
            titulo = str(ponto["nome"]).split(" - ", 1)[-1]
            if ponto.get("suite") == "base":
                titulo = str(ponto["nome"])
            self._escrever(
                "### Achado " + str(numero) + " - " + titulo,
                "",
                "- **Origem:** " + str(ponto["nome"]) + " (" + str(ponto.get("dominio")) + ", " + str(ponto.get("suite")) + ")",
                "- **História:** " + str(ponto.get("historia", "")),
                "- **O que a evidência mostra:** " + self._uma_linha(ponto.get("detalhe", "")),
            )
            if ponto.get("revisao_motivo"):
                self._escrever("- **Leitura da revisão:** " + self._uma_linha(ponto["revisao_motivo"]))
            evidencias = ponto.get("evidencias") or []
            if evidencias:
                self._escrever("- **Evidências:** " + ", ".join(self._crases(evidencias[:6])))
            self._escrever("")
        if numero == 0:
            self._escrever("Nenhuma falha de produto nesta execução.", "")

    def _lacunas_de_especificacao(self) -> None:
        achados = self._m.get("lint_historias") or []
        self._escrever("## Lacunas de especificação (lint das histórias)", "")
        if not achados:
            self._escrever("Nenhuma: toda jornada cita história existente, verifica o resultado e marca INICIO e FIM.", "")
            return
        for achado in achados:
            self._escrever("- " + str(achado))
        self._escrever("")

    def _revisao_de_validade(self) -> None:
        revisao = self._m.get("revisao")
        if not revisao:
            return
        self._escrever("## Revisão de validade e healing", "")
        auditoria = revisao.get("auditoria") or {}
        if auditoria.get("observacao"):
            self._escrever(str(auditoria["observacao"]).strip(), "")
        mudou = False
        for ponto in self._m.get("pontos") or []:
            automatico = ponto.get("veredito_automatico")
            if automatico is None:
                continue
            if automatico == ponto.get("veredito") and not ponto.get("revisao_motivo"):
                continue
            mudou = True
            self._escrever(
                "- **" + str(ponto["nome"]) + "**: " + str(automatico) + " → " + str(ponto.get("veredito"))
                + " · healing " + str(ponto.get("ciclos_de_healing", 0))
                + " — " + self._uma_linha(ponto.get("revisao_motivo", ""))
            )
        if not mudou:
            self._escrever("Todos os vereditos automáticos se confirmaram na leitura das evidências.")
        for nome in revisao.get("pontos_nao_encontrados") or []:
            self._escrever("- aviso: ponto revisado não encontrado no manifesto: " + nome)
        self._escrever("")

    def _warnings_de_comentarios(self) -> None:
        resumo = self._m.get("comentarios") or {}
        revisao = self._m.get("revisao") or {}
        julgados = revisao.get("comentarios") or []
        if not resumo and not julgados:
            return
        regra = str(resumo.get("regra") or self._config.relativo(self._config.caminho("convencao_de_comentarios")))
        violacoes = []
        aceitos = []
        for item in julgados:
            if item.get("veredito") == "violacao":
                violacoes.append(item)
            else:
                aceitos.append(item)
        self._escrever(
            "## Warnings - Convenção de comentários",
            "",
            "Regra: " + regra + " · " + str(resumo.get("total", len(julgados)))
            + " candidato(s), " + str(len(violacoes)) + " violação(ões). Warning não reprova a execução.",
            "",
        )
        if not julgados:
            self._escrever(
                "Julgamento **pendente**: candidatos em `" + str(resumo.get("arquivo", "comentarios.json"))
                + "` aguardam a leitura da etapa `/qa comentarios`.",
                "",
            )
            return
        if violacoes:
            self._escrever("| Arquivo | Linha | Categoria | O quê | Destino |", "|---|---|---|---|---|")
            for item in violacoes:
                self._escrever(
                    "| " + str(item.get("arquivo")) + " | " + str(item.get("linha"))
                    + " | " + str(item.get("categoria", "")) + " | " + self._uma_linha(item.get("o_que", ""))
                    + " | " + str(item.get("destino", "")) + " |"
                )
            self._escrever("")
        if aceitos:
            partes = []
            for item in aceitos:
                partes.append(
                    str(item.get("arquivo")) + ":" + str(item.get("linha"))
                    + " — " + self._uma_linha(item.get("porque", ""))
                )
            self._escrever("Aceitos após leitura: " + "; ".join(partes) + ".", "")

    def _criados(self) -> None:
        revisao = self._m.get("revisao") or {}
        criados = revisao.get("criados_nesta_execucao") or []
        self._escrever("## Criados nesta execução", "")
        if not criados:
            self._escrever("Nada criado — execução sobre artefatos existentes.", "")
            return
        for item in criados:
            self._escrever(
                "- `" + str(item.get("caminho")) + "` — " + self._uma_linha(item.get("o_que", ""))
                + " (derivado de: " + str(item.get("derivado_de", "?")) + ")"
            )
        self._escrever("", "Criação não é aprovação: tudo acima entra na proposta de commit para aceite.", "")

    # ── apoio ────────────────────────────────────────────────────────────

    def _selo(self, ponto: dict) -> str:
        veredito = str(ponto.get("veredito", "?"))
        automatico = ponto.get("veredito_automatico")
        if automatico and automatico != veredito:
            return "**" + veredito + "** (motor: " + str(automatico) + ")"
        return "**" + veredito + "**"

    def _uma_linha(self, texto) -> str:
        return " ".join(str(texto or "").split())

    def _crases(self, itens: list) -> list:
        convertidos = []
        for item in itens:
            convertidos.append("`" + str(item) + "`")
        return convertidos


def carregar_yaml(caminho: Path) -> dict:
    with open(caminho, encoding="utf-8") as arquivo:
        return yaml.safe_load(arquivo) or {}


def gravar_yaml(caminho: Path, conteudo: dict) -> None:
    with open(caminho, "w", encoding="utf-8") as arquivo:
        yaml.safe_dump(conteudo, arquivo, allow_unicode=True, sort_keys=False, width=100)


def gravar_json(caminho: Path, conteudo) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(conteudo, arquivo, ensure_ascii=False, indent=2, default=str)
