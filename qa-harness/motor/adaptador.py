"""Fronteira entre o motor e o projeto.

O motor não sabe como um projeto autentica, semeia dados ou quais suítes de
API ele tem. Cada projeto responde isso em `qa-harness/adaptador.py`, com uma
classe `Adaptador` que herda de `AdaptadorBase` e sobrescreve só o que precisa.
"""

import importlib.util
import sys

import requests


class SessaoDoPerfil:
    """Sessão HTTP de um perfil — autenticada, ou anônima para o visitante."""

    def __init__(self, perfil: str, identidade: str, http: requests.Session) -> None:
        self._perfil = perfil
        self._identidade = identidade
        self._http = http

    @property
    def perfil(self) -> str:
        return self._perfil

    @property
    def identidade(self) -> str:
        """Conta com que a sessão entrou (e-mail, usuário); vazia para visitante."""
        return self._identidade

    @property
    def http(self) -> requests.Session:
        """Sessão `requests` já com cookie ou cabeçalho de autenticação."""
        return self._http

    def cookies_para_navegador(self, url_app: str) -> list:
        """Converte os cookies da sessão HTTP para o formato do Playwright."""
        dominio = url_app.replace("http://", "").replace("https://", "")
        dominio = dominio.split("/")[0].split(":")[0]
        convertidos = []
        for cookie in self._http.cookies:
            convertidos.append(
                {
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": dominio,
                    "path": "/",
                    "httpOnly": False,
                    "secure": False,
                    "sameSite": "Lax",
                }
            )
        return convertidos


class AdaptadorBase:
    """Comportamento padrão; o projeto sobrescreve o que for diferente.

    Métodos que o projeto costuma implementar:
    - `autenticar(perfil)` — obrigatório se algum perfil tem conta;
    - `verificar_ambiente()` — banco, schema, contas (o motor já confere app e navegador);
    - `preparar_massa()` — estado conhecido antes das suítes;
    - `suites_de_integracao()` — classes que herdam de `motor.suite.SuiteDeIntegracao`;
    - `entrar_no_navegador(contexto, pagina, perfil)` — padrão injeta os cookies
      da sessão HTTP; projeto com login por formulário sobrescreve;
    - `limpar(limpeza)` — remove o que uma jornada criou na execução anterior.
    """

    def __init__(self, config) -> None:
        self._config = config
        self._sessoes: dict = {}

    @property
    def config(self):
        return self._config

    def verificar_ambiente(self) -> list:
        """Lista de impedimentos do ambiente do projeto (vazia = pronto)."""
        return []

    def preparar_massa(self) -> bool:
        """Recoloca o estado conhecido; devolve falso se não conseguiu."""
        return True

    def autenticar(self, perfil: str) -> SessaoDoPerfil:
        """Cria a sessão HTTP autenticada do perfil."""
        raise NotImplementedError(
            f"o adaptador do projeto não sabe autenticar o perfil '{perfil}' — "
            "implemente Adaptador.autenticar em qa-harness/adaptador.py"
        )

    def sessao(self, perfil: str) -> SessaoDoPerfil:
        """Sessão do perfil, reaproveitada durante a execução."""
        if perfil not in self._sessoes:
            if self._config.perfil_tem_conta(perfil):
                self._sessoes[perfil] = self.autenticar(perfil)
            else:
                self._sessoes[perfil] = SessaoDoPerfil(perfil, "", requests.Session())
        return self._sessoes[perfil]

    def entrar_no_navegador(self, contexto, pagina, perfil: str) -> bool:
        """Deixa o contexto do navegador com a sessão do perfil."""
        contexto.clear_cookies()
        if not self._config.perfil_tem_conta(perfil):
            return True
        cookies = self.sessao(perfil).cookies_para_navegador(self._config.url_app)
        if not cookies:
            return False
        contexto.add_cookies(cookies)
        return True

    def suites_de_integracao(self) -> list:
        """Classes de suíte de integração do projeto, na ordem de execução."""
        return []

    def limpar(self, limpeza: dict) -> None:
        """Remove registros criados por uma jornada anterior (padrão: nada)."""
        return None


def carregar_adaptador(config) -> AdaptadorBase:
    """Carrega `qa-harness/adaptador.py`; sem ele, usa o comportamento padrão."""
    caminho = config.raiz_harness / "adaptador.py"
    if not caminho.exists():
        return AdaptadorBase(config)
    raiz = str(config.raiz_harness)
    if raiz not in sys.path:
        sys.path.insert(0, raiz)
    especificacao = importlib.util.spec_from_file_location("adaptador", caminho)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    classe = getattr(modulo, "Adaptador", None)
    if classe is None:
        raise AttributeError("qa-harness/adaptador.py precisa declarar a classe Adaptador")
    return classe(config)
