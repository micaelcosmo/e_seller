"""Base das suítes de integração — toda chamada HTTP deixa evidência.

Nenhuma suíte chama `requests` direto: é aqui que request e response viram um
`.json` de caminho estável, antes de o teste poder afirmar qualquer coisa.
"""

import json

from .evidencia import ResultadoDoPonto


class RespostaObservada:
    """Uma resposta HTTP já registrada como evidência."""

    def __init__(self, status: int, corpo, texto: str, cabecalhos: dict, caminho: str) -> None:
        self._status = status
        self._corpo = corpo
        self._texto = texto
        self._cabecalhos = cabecalhos
        self._caminho = caminho

    @property
    def status(self) -> int:
        return self._status

    @property
    def corpo(self):
        """Corpo desserializado quando era JSON; `None` quando não era."""
        return self._corpo

    @property
    def texto(self) -> str:
        """Corpo cru — útil para procurar uma marca dentro de HTML."""
        return self._texto

    @property
    def cabecalhos(self) -> dict:
        return self._cabecalhos

    @property
    def caminho_evidencia(self) -> str:
        return self._caminho


class SuiteDeIntegracao:
    """Base comum das suítes de API: sessão por perfil, chamada e evidência.

    Cada suíte declara `dominio` e implementa `executar()`, que devolve a lista
    de `ResultadoDoPonto`. Os nomes de ponto e de história vêm do plano em
    `spec/test/planos/<dominio>.yaml`.
    """

    LIMITE_DE_TEXTO_NA_EVIDENCIA = 4000

    dominio = "indefinido"

    def __init__(self, config, adaptador, registrador) -> None:
        self._config = config
        self._adaptador = adaptador
        self._registrador = registrador

    def executar(self) -> list:
        raise NotImplementedError

    def _novo_ponto(self, nome: str, historia: str) -> ResultadoDoPonto:
        return ResultadoDoPonto(nome, historia, "integracao", self.dominio)

    def _chamar(
        self,
        ponto: ResultadoDoPonto,
        perfil: str,
        metodo: str,
        caminho: str,
        acao: str,
        corpo_json=None,
        seguir_redirecionamento: bool = False,
        procurar: list = None,
    ) -> RespostaObservada:
        """Executa a chamada com a sessão do perfil e grava a evidência.

        `procurar` lista textos que o ponto confere no corpo: a evidência grava
        quantas vezes cada um aparece no corpo INTEIRO — o recorte guardado não
        prova presença nem ausência em página grande.
        """
        sessao = self._adaptador.sessao(perfil)
        url = self._config.url_api + caminho
        resposta = sessao.http.request(
            metodo,
            url,
            json=corpo_json,
            allow_redirects=seguir_redirecionamento,
            timeout=max(30, self._config.timeout_ms // 1000 * 4),
        )
        corpo = self._desserializar(resposta)
        requisicao = {
            "metodo": metodo,
            "url": url,
            "perfil": perfil,
            "identidade_do_perfil": sessao.identidade,
            "corpo_enviado": corpo_json,
        }
        registro = {
            "status": resposta.status_code,
            "cabecalho_location": resposta.headers.get("location"),
            "tipo_de_conteudo": resposta.headers.get("content-type"),
            "tamanho_do_corpo": len(resposta.text),
        }
        if procurar:
            ocorrencias = {}
            for texto in procurar:
                ocorrencias[str(texto)] = resposta.text.count(str(texto))
            registro["procurado_no_corpo_inteiro"] = ocorrencias
        registro["corpo_json"] = corpo
        registro["corpo_texto_recortado"] = self._recortar(resposta.text, corpo)
        caminho_evidencia = self._registrador.gravar_chamada_de_api(
            self.dominio, acao, requisicao, registro, ponto.nome
        )
        ponto.anotar_evidencia(caminho_evidencia)
        return RespostaObservada(
            resposta.status_code,
            corpo,
            resposta.text,
            dict(resposta.headers),
            caminho_evidencia,
        )

    def _desserializar(self, resposta):
        tipo = resposta.headers.get("content-type", "")
        if "application/json" not in tipo:
            return None
        try:
            return resposta.json()
        except (json.JSONDecodeError, ValueError):
            return None

    def _recortar(self, texto: str, corpo) -> str:
        """Recorte do corpo cru quando ele não era JSON — prova sem virar despejo."""
        if corpo is not None:
            return ""
        return texto[: self.LIMITE_DE_TEXTO_NA_EVIDENCIA]
