"""Vereditos por ponto e gravação das evidências de API.

Duas regras do contrato de evidências valem aqui em tempo de execução:
1. Só `.png` e `.json`. Dump de stdout (`.txt`) é recusado.
2. Dois pontos distintos não citam o mesmo arquivo — o segundo uso levanta erro.
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

VEREDITOS = [
    "VALIDO",
    "FALHA DE PRODUTO",
    "EVIDENCIA INVALIDA",
    "INCONCLUSIVO",
]


class ResultadoDoPonto:
    """Veredito de um ponto, com as evidências que o sustentam."""

    def __init__(
        self,
        nome: str,
        historia: str,
        suite: str,
        dominio: str,
        viewport: str = "",
    ) -> None:
        self._nome = nome
        self._historia = historia
        self._suite = suite
        self._dominio = dominio
        self._viewport = viewport
        self._veredito = "INCONCLUSIVO"
        self._detalhe = ""
        self._evidencias: list = []
        self._percurso: list = []
        self._ciclos_de_healing = 0
        self._extra: dict = {}

    @property
    def nome(self) -> str:
        """`Ponto <n> - <título>` ou `Jornada - <nome>`."""
        return self._nome

    @property
    def historia(self) -> str:
        return self._historia

    @property
    def suite(self) -> str:
        """integracao · jornada · base · ou o nome de uma linha do projeto."""
        return self._suite

    @property
    def dominio(self) -> str:
        return self._dominio

    @property
    def veredito(self) -> str:
        return self._veredito

    @property
    def detalhe(self) -> str:
        return self._detalhe

    @property
    def evidencias(self) -> list:
        return self._evidencias

    @property
    def percurso(self) -> list:
        return self._percurso

    def anotar_evidencia(self, caminho_relativo: str) -> None:
        """Associa uma evidência já gravada a este ponto."""
        if caminho_relativo not in self._evidencias:
            self._evidencias.append(caminho_relativo)

    def anotar_passo(
        self, ordem: int, marco: str, rotulo: str, captura: str, observado: dict
    ) -> None:
        """Registra um passo do caminho percorrido, com a captura dele."""
        self._percurso.append(
            {
                "ordem": ordem,
                "marco": marco,
                "rotulo": rotulo,
                "captura": captura,
                "observado": observado,
            }
        )
        self.anotar_evidencia(captura)

    def anotar_extra(self, chave: str, valor) -> None:
        """Dado auxiliar que vai ao manifesto (erros de console, problemas...)."""
        self._extra[chave] = valor

    def registrar_ciclo_de_healing(self) -> None:
        self._ciclos_de_healing = self._ciclos_de_healing + 1

    def concluir(self, veredito: str, detalhe: str) -> None:
        """Fecha o ponto com um dos vereditos permitidos."""
        if veredito not in VEREDITOS:
            raise ValueError(
                "veredito inválido: " + veredito + " — permitidos: " + ", ".join(VEREDITOS)
            )
        self._veredito = veredito
        self._detalhe = detalhe

    def para_manifesto(self) -> dict:
        """Forma serializável consumida pelo manifesto, relatório e PDF."""
        registro = {
            "nome": self._nome,
            "historia": self._historia,
            "dominio": self._dominio,
            "suite": self._suite,
            "viewport": self._viewport,
            "veredito": self._veredito,
            "detalhe": self._detalhe,
            "ciclos_de_healing": self._ciclos_de_healing,
            "percurso": list(self._percurso),
            "evidencias": list(self._evidencias),
        }
        for chave in self._extra:
            registro[chave] = self._extra[chave]
        return registro


def ponto_de_dicionario(dados: dict) -> ResultadoDoPonto:
    """Reconstrói um ponto a partir do formato do manifesto (linhas do projeto)."""
    ponto = ResultadoDoPonto(
        str(dados.get("nome", "")),
        str(dados.get("historia", "")),
        str(dados.get("suite", "")),
        str(dados.get("dominio", "")),
        str(dados.get("viewport", "")),
    )
    for caminho in dados.get("evidencias") or []:
        ponto.anotar_evidencia(caminho)
    for passo in dados.get("percurso") or []:
        ponto._percurso.append(dict(passo))
    ciclos = int(dados.get("ciclos_de_healing") or 0)
    contador = 0
    while contador < ciclos:
        ponto.registrar_ciclo_de_healing()
        contador = contador + 1
    veredito = str(dados.get("veredito") or "INCONCLUSIVO")
    if veredito not in VEREDITOS:
        veredito = "INCONCLUSIVO"
    ponto.concluir(veredito, str(dados.get("detalhe") or ""))
    return ponto


class RegistradorDeEvidencias:
    """Escreve as evidências de API e confere o contrato da pasta."""

    EXTENSOES_PERMITIDAS = [".png", ".json"]

    def __init__(self, config) -> None:
        self._config = config
        self._raiz = config.caminho("evidencias")
        self._caminhos_usados: dict = {}
        self._ordem_por_dominio: dict = {}

    @property
    def raiz(self) -> Path:
        return self._raiz

    def gravar_chamada_de_api(
        self, dominio: str, acao: str, requisicao: dict, resposta: dict, dono: str
    ) -> str:
        """Grava request e response completos de uma chamada, numerados por domínio."""
        ordem = self._proxima_ordem(dominio)
        destino = self._raiz / "api" / dominio / (self._numerar(ordem, acao) + ".json")
        conteudo = {
            "gravado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "ponto": dono,
            "acao": acao,
            "requisicao": requisicao,
            "resposta": resposta,
        }
        self._conferir_extensao(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        with open(destino, "w", encoding="utf-8") as arquivo:
            json.dump(conteudo, arquivo, ensure_ascii=False, indent=2, default=str)
        caminho = self._config.relativo(destino)
        self.reservar(caminho, dono)
        return caminho

    def reservar(self, caminho_relativo: str, dono: str) -> None:
        """Marca o arquivo como prova de um ponto; recusa o segundo dono."""
        self._conferir_extensao(Path(caminho_relativo))
        anterior = self._caminhos_usados.get(caminho_relativo)
        if anterior is not None and anterior != dono:
            raise ValueError(
                "evidência compartilhada por dois pontos distintos: "
                + caminho_relativo
                + " (já usada por "
                + anterior
                + ")"
            )
        self._caminhos_usados[caminho_relativo] = dono

    def _proxima_ordem(self, dominio: str) -> int:
        """Numeração estável por domínio; a primeira chamada limpa a pasta antiga."""
        if dominio not in self._ordem_por_dominio:
            pasta = self._raiz / "api" / dominio
            if pasta.exists():
                shutil.rmtree(pasta)
            self._ordem_por_dominio[dominio] = 0
        self._ordem_por_dominio[dominio] = self._ordem_por_dominio[dominio] + 1
        return self._ordem_por_dominio[dominio]

    def _conferir_extensao(self, destino: Path) -> None:
        if destino.suffix not in self.EXTENSOES_PERMITIDAS:
            raise ValueError(
                "extensão de evidência proibida: "
                + destino.suffix
                + " — permitidas: "
                + ", ".join(self.EXTENSOES_PERMITIDAS)
            )

    def _numerar(self, ordem: int, nome: str) -> str:
        """Prefixo numérico estável: `01-nome-da-acao`."""
        limpo = criar_apelido(nome, 60)
        return str(ordem).zfill(2) + "-" + limpo


def criar_apelido(texto: str, limite: int) -> str:
    """Nome de arquivo ASCII, minúsculo e com hífens (o rótulo legível vai no JSON)."""
    import unicodedata

    sem_acento = unicodedata.normalize("NFKD", str(texto))
    sem_acento = sem_acento.encode("ascii", "ignore").decode("ascii").lower()
    limpo = ""
    for caractere in sem_acento:
        if caractere.isalnum():
            limpo = limpo + caractere
        elif caractere in [" ", "-", "_", "/", "."]:
            limpo = limpo + "-"
    while "--" in limpo:
        limpo = limpo.replace("--", "-")
    return limpo.strip("-")[:limite].strip("-")
