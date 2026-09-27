"""Adaptador do e_seller para o motor agnóstico da skill /qa.

O motor sabe executar suítes, jornadas, base visual, relatório e PDF; aqui fica o
que só o e_seller sabe: onde estão as credenciais locais da stack de QA, como uma
conta autentica (form OAuth2 em `/api/v1/auth/token`), como o navegador "entra"
(SPA lê o JWT do localStorage; o painel `/admin` usa o formulário do SQLAdmin) e
como o banco volta ao estado conhecido (massa_de_dados.py).
"""

import requests

from ambiente.credenciais import CredenciaisLocais
from massa_de_dados import MassaDeDados
from motor.adaptador import AdaptadorBase, SessaoDoPerfil


class Adaptador(AdaptadorBase):
    """Autenticação, massa de dados, verificações e suítes do e_seller."""

    CHAVE_DA_SENHA_POR_PERFIL = {
        "cliente": "QA_CLIENTE_PASSWORD",
        "sem_compras": "QA_SEM_COMPRAS_PASSWORD",
        "admin": "QA_ADMIN_PASSWORD",
    }

    def __init__(self, config) -> None:
        """Liga as credenciais locais e a massa; os tokens da massa ficam em memória."""
        super().__init__(config)
        self.credenciais = CredenciaisLocais(config.raiz_harness / "ambiente" / "credenciais-locais.env")
        self.massa = MassaDeDados(config, self.credenciais)
        self.tokens_da_massa: dict = {}
        self.admin_entrou_no_painel = None

    # ── endereços ────────────────────────────────────────────────────────

    @property
    def url_backend(self) -> str:
        """Backend da stack de QA direto (sem o nginx) — só para login e saúde."""
        return str((self.config.dados.get("ambiente") or {}).get("backend", "")).rstrip("/")

    # ── ambiente ─────────────────────────────────────────────────────────

    def verificar_ambiente(self) -> list:
        """Credenciais locais, saúde do backend, banco/seed e login de cada perfil."""
        impedimentos = []
        if not self.credenciais.existe():
            return ["stack de QA nunca subiu nesta máquina: python qa-harness/ambiente/stack.py subir"]
        try:
            saude = requests.get(self.url_backend + "/health", timeout=10)
            if saude.status_code != 200 or saude.json().get("db") != "ok":
                impedimentos.append("backend de QA sem banco: /health respondeu " + str(saude.status_code))
        except requests.RequestException as erro:
            impedimentos.append("backend de QA fora do ar: " + type(erro).__name__)
            return impedimentos
        for impedimento in self.massa.impedimentos():
            impedimentos.append(impedimento)
        if impedimentos:
            return impedimentos
        try:
            self.preparar_massa()
        except Exception as erro:
            impedimentos.append("massa de dados falhou: " + type(erro).__name__ + ": " + str(erro)[:160])
            return impedimentos
        for perfil in self.config.perfis_com_conta():
            try:
                self.sessao(perfil)
            except Exception as erro:
                impedimentos.append("conta do perfil '" + perfil + "' não autentica: " + str(erro)[:160])
        return impedimentos

    def preparar_massa(self) -> bool:
        """Recoloca o banco de QA no estado conhecido (ver massa_de_dados.py)."""
        self.tokens_da_massa = self.massa.preparar()
        return True

    def token_da_massa(self, nome: str) -> str:
        """Token de download (ou referência) criado pela massa desta execução."""
        if not self.tokens_da_massa:
            self.preparar_massa()
        return str(self.tokens_da_massa.get(nome, ""))

    # ── autenticação ─────────────────────────────────────────────────────

    def senha(self, perfil: str) -> str:
        """Senha local do perfil (nunca impressa nem gravada em evidência)."""
        return self.credenciais.valor(self.CHAVE_DA_SENHA_POR_PERFIL[perfil])

    def autenticar(self, perfil: str) -> SessaoDoPerfil:
        """Login OAuth2 (form) direto no backend; a sessão leva o Bearer para o nginx."""
        conta = str(self.config.perfil(perfil)["conta"])
        resposta = requests.post(
            self.url_backend + "/api/v1/auth/token",
            data={"username": conta, "password": self.senha(perfil)},
            timeout=30,
        )
        if resposta.status_code != 200:
            raise RuntimeError("login de " + conta + " respondeu " + str(resposta.status_code))
        corpo = resposta.json()
        http = requests.Session()
        http.headers["Authorization"] = "Bearer " + str(corpo["access_token"])
        sessao = SessaoDoPerfil(perfil, conta, http)
        sessao.tokens = {"access_token": corpo["access_token"], "refresh_token": corpo.get("refresh_token", "")}
        return sessao

    # ── navegador ────────────────────────────────────────────────────────

    def entrar_no_navegador(self, contexto, pagina, perfil: str) -> bool:
        """Deixa o navegador com a sessão do perfil, como o SPA e o /admin guardam.

        SPA: `localStorage` com `token`, `refresh_token` e `email` (o que o login do
        modal grava). Admin: além disso, login pelo formulário do SQLAdmin em
        `/admin/login` — o caminho real de um administrador no navegador.
        """
        contexto.clear_cookies()
        pagina.goto(self.config.url_app + "/", wait_until="domcontentloaded",
                    timeout=self.config.timeout_de_navegacao_ms)
        pagina.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        if not self.config.perfil_tem_conta(perfil):
            self._sair_da_pagina(pagina)
            return True
        sessao = self.sessao(perfil)
        pagina.evaluate(
            "([token, refresh, email]) => {"
            " localStorage.setItem('token', token);"
            " localStorage.setItem('refresh_token', refresh);"
            " localStorage.setItem('email', email); }",
            [sessao.tokens["access_token"], sessao.tokens["refresh_token"], sessao.identidade],
        )
        if perfil == "admin":
            entrou = self._entrar_no_painel_admin(pagina)
            self._sair_da_pagina(pagina)
            return entrou
        self._sair_da_pagina(pagina)
        return True

    def _sair_da_pagina(self, pagina) -> None:
        """Deixa a aba em branco: o próximo `abrir` carrega o SPA do zero, já com a sessão.

        Sem isso, abrir `/#/...` a partir de `/` só troca o hash e o SPA segue com o
        estado de antes do login (botões da conta escondidos).
        """
        pagina.goto("about:blank")

    def _entrar_no_painel_admin(self, pagina) -> bool:
        """Preenche o formulário de login do SQLAdmin; falso só se o formulário não existe."""
        pagina.goto(self.config.url_app + "/admin/login", wait_until="domcontentloaded",
                    timeout=self.config.timeout_de_navegacao_ms)
        campo_usuario = pagina.locator("input[name=username]")
        if campo_usuario.count() == 0:
            return False
        campo_usuario.first.fill(str(self.config.perfil("admin")["conta"]))
        pagina.locator("input[name=password]").first.fill(self.senha("admin"))
        pagina.locator("button[type=submit], input[type=submit]").first.click()
        pagina.wait_for_load_state("domcontentloaded")
        self.admin_entrou_no_painel = "/admin/login" not in pagina.url
        return True

    def limpar(self, limpeza: dict) -> None:
        """Limpeza declarada na jornada (carrinho, favoritos, avaliação, pedidos pendentes)."""
        self.massa.limpar(limpeza)

    # ── suítes ───────────────────────────────────────────────────────────

    def suites_de_integracao(self) -> list:
        """Suítes de `qa-harness/testes/api/`, na ordem em que a pessoa encontra o produto."""
        from testes.api.teste_vitrine import SuiteVitrine
        from testes.api.teste_acesso import SuiteAcesso
        from testes.api.teste_compra import SuiteCompra
        from testes.api.teste_biblioteca import SuiteBiblioteca
        from testes.api.teste_administracao import SuiteAdministracao

        return [SuiteVitrine, SuiteAcesso, SuiteCompra, SuiteBiblioteca, SuiteAdministracao]
