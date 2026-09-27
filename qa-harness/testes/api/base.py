"""Base das suítes de integração do e_seller — evidência sem segredo.

O motor grava request e response inteiros no `.json` de evidência, que vai para o
git. Senha enviada e token recebido não podem ir junto: esta base reescreve o
arquivo logo depois da gravação, trocando o valor de toda chave sensível por um
marcador que diz que o valor existia e o tamanho dele (a prova continua de pé), e
trocando também, em qualquer texto, os valores secretos já conhecidos (um token de
download aparece dentro de URLs).

Além do `_chamar` do motor (JSON com a sessão de um perfil), o e_seller precisa de
formulário (login OAuth2, simulador de pagamento, login do SQLAdmin), upload e
sessão avulsa (conta criada na própria suíte): `_chamar_http` grava a evidência do
mesmo jeito que o motor.
"""

import json
import re
import time

import requests

from motor.suite import RespostaObservada, SuiteDeIntegracao


class MascaradorDeSegredos:
    """Troca valores sensíveis por um marcador, em qualquer profundidade."""

    PARTES_SENSIVEIS = ("password", "senha", "token", "secret", "authorization", "totp", "otp_code")
    PADROES_EM_TEXTO = [
        (re.compile(r"(/api/v1/download/)[A-Za-z0-9_\-]{16,}"), r"\g<1>[mascarado]"),
        (re.compile(r'(name="csrf_token" value=")[^"]+(")'), r"\g<1>[mascarado]\g<2>"),
    ]

    def __init__(self) -> None:
        """Começa sem valores secretos conhecidos; a suíte registra os que descobre."""
        self.valores_secretos: set = set()

    def registrar(self, valor) -> None:
        """Passa a mascarar este valor em qualquer texto da evidência."""
        if valor and len(str(valor)) >= 8:
            self.valores_secretos.add(str(valor))

    def chave_sensivel(self, chave: str) -> bool:
        """A chave carrega segredo (senha, token, segredo de TOTP...)?"""
        minuscula = str(chave).lower()
        for parte in self.PARTES_SENSIVEIS:
            if parte in minuscula:
                return True
        return False

    def marcador(self, valor) -> str:
        """Texto que prova a presença do valor sem revelá-lo."""
        if valor is None or valor == "":
            return "[vazio]"
        return "[mascarado: " + str(len(str(valor))) + " caracteres]"

    def coletar(self, dado) -> None:
        """Registra como secreto todo valor de chave sensível encontrado no dado."""
        if isinstance(dado, dict):
            for chave in dado:
                valor = dado[chave]
                if self.chave_sensivel(chave) and isinstance(valor, str):
                    self.registrar(valor)
                else:
                    self.coletar(valor)
        elif isinstance(dado, list):
            for item in dado:
                self.coletar(item)

    def mascarar(self, dado):
        """Cópia do dado com os valores sensíveis mascarados."""
        if isinstance(dado, dict):
            copia = {}
            for chave in dado:
                if self.chave_sensivel(chave) and not isinstance(dado[chave], (dict, list)):
                    copia[chave] = self.marcador(dado[chave])
                else:
                    copia[chave] = self.mascarar(dado[chave])
            return copia
        if isinstance(dado, list):
            itens = []
            for item in dado:
                itens.append(self.mascarar(item))
            return itens
        if isinstance(dado, str):
            texto = dado
            for segredo in self.valores_secretos:
                if segredo in texto:
                    texto = texto.replace(segredo, "[mascarado]")
            for padrao, troca in self.PADROES_EM_TEXTO:
                texto = padrao.sub(troca, texto)
            return texto
        return dado


class SuiteDoEseller(SuiteDeIntegracao):
    """Suíte do e_seller: toda evidência de API sai com segredos mascarados."""

    LIMITE_DO_RECORTE = 4000

    def __init__(self, config, adaptador, registrador) -> None:
        """Mesma assinatura do motor; acrescenta o mascarador e a marca da execução."""
        super().__init__(config, adaptador, registrador)
        self._mascarador = MascaradorDeSegredos()
        self._marca = getattr(registrador, "execucao", "") or self._marca_local()

    def _marca_local(self) -> str:
        """Marca curta desta execução, para nomes únicos (e-mails, cupons, títulos)."""
        return time.strftime("%d%H%M%S")

    # ── chamadas ─────────────────────────────────────────────────────────

    def _chamar(
        self,
        ponto,
        perfil: str,
        metodo: str,
        caminho: str,
        acao: str,
        corpo_json=None,
        seguir_redirecionamento: bool = False,
        procurar: list = None,
    ) -> RespostaObservada:
        """Chama pelo motor (que grava a evidência) e mascara o arquivo gravado."""
        self._mascarador.coletar(corpo_json)
        resposta = super()._chamar(
            ponto, perfil, metodo, caminho, acao, corpo_json, seguir_redirecionamento, procurar
        )
        self._mascarador.coletar(resposta.corpo)
        self._mascarar_arquivo(resposta.caminho_evidencia)
        return resposta

    def _chamar_http(
        self,
        ponto,
        http: requests.Session,
        identidade: str,
        metodo: str,
        caminho: str,
        acao: str,
        json_corpo=None,
        formulario: dict = None,
        arquivos: dict = None,
        seguir_redirecionamento: bool = False,
        procurar: list = None,
        base: str = "",
    ) -> RespostaObservada:
        """Chamada com sessão avulsa (form, upload, cookie); grava evidência como o motor."""
        url = (base or self._config.url_api) + caminho
        self._mascarador.coletar(json_corpo)
        self._mascarador.coletar(formulario)
        resposta = http.request(
            metodo,
            url,
            json=json_corpo,
            data=formulario,
            files=arquivos,
            allow_redirects=seguir_redirecionamento,
            timeout=60,
        )
        corpo = self._desserializar(resposta)
        self._mascarador.coletar(corpo)
        enviado = json_corpo
        if formulario is not None:
            enviado = {"formulario": formulario}
        if arquivos is not None:
            nomes = []
            for campo in arquivos:
                nomes.append(campo + "=" + str(arquivos[campo][0]))
            enviado = {"arquivos": nomes}
        requisicao = {
            "metodo": metodo,
            "url": url,
            "perfil": "sessao-avulsa",
            "identidade_do_perfil": identidade,
            "corpo_enviado": enviado,
        }
        registro = {
            "status": resposta.status_code,
            "cabecalho_location": resposta.headers.get("location"),
            "tipo_de_conteudo": resposta.headers.get("content-type"),
            "content_disposition": resposta.headers.get("content-disposition"),
            "tamanho_do_corpo": len(resposta.content),
        }
        if procurar:
            ocorrencias = {}
            for texto in procurar:
                ocorrencias[str(texto)] = resposta.text.count(str(texto))
            registro["procurado_no_corpo_inteiro"] = ocorrencias
        registro["corpo_json"] = corpo
        registro["corpo_texto_recortado"] = "" if corpo is not None else resposta.text[: self.LIMITE_DO_RECORTE]
        caminho_evidencia = self._registrador.gravar_chamada_de_api(
            self.dominio, acao, requisicao, registro, ponto.nome
        )
        ponto.anotar_evidencia(caminho_evidencia)
        self._mascarar_arquivo(caminho_evidencia)
        return RespostaObservada(resposta.status_code, corpo, resposta.text, dict(resposta.headers), caminho_evidencia)

    def _desserializar(self, resposta):
        """Corpo JSON também quando o tipo é `application/problem+json` (erros do e_seller)."""
        tipo = str(resposta.headers.get("content-type", "")).lower()
        if "json" not in tipo:
            return None
        try:
            return resposta.json()
        except ValueError:
            return None

    def _mascarar_arquivo(self, caminho_relativo: str) -> None:
        """Reescreve o `.json` de evidência com os segredos mascarados."""
        arquivo = self._config.raiz_projeto / caminho_relativo
        with open(arquivo, encoding="utf-8") as leitura:
            conteudo = json.load(leitura)
        mascarado = self._mascarador.mascarar(conteudo)
        with open(arquivo, "w", encoding="utf-8") as escrita:
            json.dump(mascarado, escrita, ensure_ascii=False, indent=2, default=str)

    # ── apoio ────────────────────────────────────────────────────────────

    def _segredo(self, valor: str) -> str:
        """Registra um valor como secreto (ex.: token de download da massa) e o devolve."""
        self._mascarador.registrar(valor)
        return valor

    def _conta(self, perfil: str) -> str:
        """E-mail da conta do perfil, como declarado no config.yaml."""
        return str(self._config.perfil(perfil).get("conta") or "")

    def _slugs(self, corpo) -> list:
        """Slugs de uma lista de produtos (vazia quando o corpo não é lista)."""
        encontrados = []
        if not isinstance(corpo, list):
            return encontrados
        for item in corpo:
            if isinstance(item, dict) and "slug" in item:
                encontrados.append(item["slug"])
        return encontrados

    def _detalhe(self, resposta: RespostaObservada) -> str:
        """Mensagem `detail` de um erro da API (vazia quando não há)."""
        if isinstance(resposta.corpo, dict):
            return str(resposta.corpo.get("detail", ""))
        return ""

    def _cabecalho(self, resposta: RespostaObservada, nome: str) -> str:
        """Valor de um cabeçalho sem diferenciar caixa (o nginx manda `Content-Type`)."""
        procurado = nome.lower()
        for chave in resposta.cabecalhos:
            if str(chave).lower() == procurado:
                return str(resposta.cabecalhos[chave])
        return ""

    def _nova_sessao(self) -> requests.Session:
        """Sessão HTTP sem autenticação, com seus próprios cookies."""
        return requests.Session()

    def _sessao_com_token(self, token: str) -> requests.Session:
        """Sessão HTTP com um Bearer avulso (conta criada pela própria suíte)."""
        http = requests.Session()
        http.headers["Authorization"] = "Bearer " + token
        self._segredo(token)
        return http
