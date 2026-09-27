"""Leitura das especificações de teste do projeto.

O relatório não redige nada livremente: a história de usuário, os critérios de
aceite, as pré-condições e a validade de cada ponto vêm de `spec/test/` e são
lidos daqui. O PDF é uma projeção dessas fontes mais o manifesto da execução.

Formato das histórias (`spec/test/historias/<dominio>.md`):
- cabeçalho do arquivo com `**Jornadas:** <caminho>` quando o domínio tem tela;
- `## História <n> - <assunto>`, `**Como** ..., **quero** ..., **para** ...`,
  `**Fontes:** ...`, critérios como `- [ ] ...`;
- `**Prova visual:** não se aplica — <motivo>` dispensa a jornada de uma história.
"""

import re
from pathlib import Path

import yaml

PADRAO_TITULO = re.compile(r"^## (História \d+ - .+?)\s*$", re.M)


def normalizar(nome: str) -> str:
    """Chave de busca tolerante a espaço e caixa."""
    return " ".join(str(nome).split()).lower()


class HistoriaDeUsuario:
    """Uma história lida de `spec/test/historias/<dominio>.md`."""

    def __init__(self, nome: str, dominio: str, arquivo: Path) -> None:
        self.nome = nome
        self.dominio = dominio
        self.arquivo = arquivo
        self.papel = ""
        self.quero = ""
        self.para = ""
        self.fontes = ""
        self.criterios: list = []
        self.prova_visual_dispensada = ""

    @property
    def narrativa(self) -> str:
        """A frase completa, no formato Como/quero/para."""
        if not self.papel:
            return ""
        if not self.quero:
            return self.papel
        return "Como " + self.papel + ", quero " + self.quero + ", para " + self.para + "."


class ArquivoDeHistorias:
    """Um arquivo de histórias de um domínio, com o cabeçalho lido."""

    def __init__(self, caminho: Path) -> None:
        self.caminho = caminho
        self.dominio = caminho.stem
        self.texto = caminho.read_text(encoding="utf-8")
        self.jornadas = self._ler_campo_do_cabecalho("Jornadas")

    def _ler_campo_do_cabecalho(self, campo: str) -> str:
        cabecalho = self.texto.split("\n## ", 1)[0]
        encontrado = re.search(r"\*\*" + campo + r":\*\*\s*`?([^`·\n]+)`?", cabecalho)
        if not encontrado:
            return ""
        return encontrado.group(1).strip()

    @property
    def tem_tela(self) -> bool:
        """Domínio que declara arquivo de jornadas é domínio com tela."""
        return bool(self.jornadas)


class PontoDePlano:
    """Um ponto lido de `spec/test/planos/<dominio>.yaml`."""

    def __init__(self, dados: dict, dominio: str, arquivo: Path) -> None:
        self.nome = str(dados.get("nome", ""))
        self.historia = str(dados.get("historia", ""))
        self.suite = str(dados.get("suite", ""))
        self.dominio = dominio
        self.arquivo = arquivo
        self.validade = str(dados.get("validade", "")).strip()
        self.pre_condicoes = dados.get("pre_condicoes") or []
        self.fluxo = dados.get("fluxo") or []
        self.limitacoes_ambiente = dados.get("limitacoes_ambiente") or []


class Especificacao:
    """Índice das histórias, planos, jornadas e do catálogo da base visual."""

    def __init__(self, config) -> None:
        self._config = config
        self._arquivos_de_historias: dict = {}
        self._historias: dict = {}
        self._pontos: dict = {}
        self._pontos_por_dominio: dict = {}
        self._carregar_historias()
        self._carregar_planos()

    # ── consultas ────────────────────────────────────────────────────────

    def historia(self, nome: str):
        """A história com aquele título, ou `None`."""
        return self._historias.get(normalizar(nome))

    def historias(self) -> list:
        """Todas as histórias, na ordem dos arquivos."""
        return list(self._historias.values())

    def arquivos_de_historias(self) -> dict:
        """{dominio: ArquivoDeHistorias}."""
        return self._arquivos_de_historias

    def ponto(self, nome: str, dominio: str = ""):
        """O ponto de plano com aquele nome (no domínio, quando informado)."""
        if dominio:
            encontrado = self._pontos_por_dominio.get((dominio, normalizar(nome)))
            if encontrado is not None:
                return encontrado
        return self._pontos.get(normalizar(nome))

    def pontos_de_plano(self) -> list:
        return list(self._pontos_por_dominio.values())

    def jornadas(self) -> list:
        """Jornadas declaradas, cada uma com `_dominio` e `_arquivo`."""
        pasta = self._config.caminho("jornadas")
        declaradas = []
        if not pasta.exists():
            return declaradas
        for arquivo in sorted(pasta.glob("*.yaml")):
            if arquivo.name.startswith("_"):
                continue
            dados = yaml.safe_load(arquivo.read_text(encoding="utf-8")) or {}
            dominio = str(dados.get("dominio") or arquivo.stem)
            for jornada in dados.get("jornadas") or []:
                copia = dict(jornada)
                copia["_dominio"] = dominio
                copia["_arquivo"] = self._config.relativo(arquivo)
                declaradas.append(copia)
        return declaradas

    def catalogo_da_base_visual(self) -> dict:
        """Perfis e telas do retrato do sistema; vazio se o catálogo não existe."""
        caminho = self._config.caminho("base_visual")
        if not caminho.exists():
            return {}
        return yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}

    # ── carga ────────────────────────────────────────────────────────────

    def _carregar_historias(self) -> None:
        pasta = self._config.caminho("historias")
        if not pasta.exists():
            return
        for caminho in sorted(pasta.glob("*.md")):
            if caminho.name.startswith("_"):
                continue
            arquivo = ArquivoDeHistorias(caminho)
            self._arquivos_de_historias[arquivo.dominio] = arquivo
            blocos = arquivo.texto.split("\n## ")
            for bloco in blocos[1:]:
                linhas = bloco.split("\n")
                nome = linhas[0].strip()
                if not nome.startswith("História"):
                    continue
                historia = HistoriaDeUsuario(nome, arquivo.dominio, caminho)
                self._preencher_historia(historia, linhas[1:])
                self._historias[normalizar(nome)] = historia

    def _preencher_historia(self, historia: HistoriaDeUsuario, linhas: list) -> None:
        for linha in linhas:
            limpa = linha.strip()
            if limpa.startswith("**Como**"):
                self._extrair_narrativa(historia, limpa)
            elif limpa.startswith("**Fontes:**"):
                historia.fontes = self._sem_marcacao(limpa.replace("**Fontes:**", ""))
            elif limpa.startswith("**Prova visual:**"):
                historia.prova_visual_dispensada = self._sem_marcacao(
                    limpa.replace("**Prova visual:**", "")
                )
            elif limpa.startswith("- [ ]") or limpa.startswith("- [x]"):
                historia.criterios.append(self._sem_marcacao(limpa[5:]))

    def _extrair_narrativa(self, historia: HistoriaDeUsuario, linha: str) -> None:
        texto = self._sem_marcacao(linha)
        padrao = re.compile(r"^Como\s+(.*?),\s*quero\s+(.*?),\s*para\s+(.*?)\.?$")
        encontrado = padrao.match(texto)
        if not encontrado:
            historia.papel = texto
            return
        historia.papel = encontrado.group(1).strip()
        historia.quero = encontrado.group(2).strip()
        historia.para = encontrado.group(3).strip()

    def _carregar_planos(self) -> None:
        pasta = self._config.caminho("planos")
        if not pasta.exists():
            return
        for arquivo in sorted(pasta.glob("*.yaml")):
            if arquivo.name.startswith("_"):
                continue
            dados = yaml.safe_load(arquivo.read_text(encoding="utf-8")) or {}
            dominio = str(dados.get("dominio") or arquivo.stem)
            for bruto in dados.get("pontos") or []:
                ponto = PontoDePlano(bruto, dominio, arquivo)
                self._pontos[normalizar(ponto.nome)] = ponto
                self._pontos_por_dominio[(dominio, normalizar(ponto.nome))] = ponto

    def _sem_marcacao(self, texto: str) -> str:
        limpo = str(texto).replace("**", "").replace("`", "")
        return limpo.strip()
