"""Suíte de integração — domínio acesso (cadastro, login, logout, perfil fiscal).

Implementa os pontos de `.spec/test/planos/acesso.yaml`. A conta usada aqui é
criada pela própria suíte (`qa-novo-api-<execução>`), com senha descartável da
execução — nunca a senha de uma conta de perfil do config.yaml.
"""

from testes.api.base import SuiteDoEseller

HISTORIA_CADASTRO = "História 1 - Visitante cria uma conta de comprador"
HISTORIA_LOGIN = "História 2 - Comprador entra e sai da conta"
HISTORIA_PERFIL = "História 3 - Comprador mantém o perfil fiscal"


class SuiteAcesso(SuiteDoEseller):
    """Cadastro, recusa de duplicado, login, senha errada, logout e perfil fiscal."""

    dominio = "acesso"

    def __init__(self, config, adaptador, registrador) -> None:
        """Define a conta descartável desta execução."""
        super().__init__(config, adaptador, registrador)
        self.email = "qa-novo-api-" + self._marca + "@eseller-qa.test"
        self.senha_descartavel = "qa-senha-" + self._marca
        self.token = ""

    def executar(self) -> list:
        """Executa os pontos na ordem do plano (cada um depende do anterior)."""
        pontos = []
        pontos.append(self._ponto_cadastro())
        pontos.append(self._ponto_duplicado())
        pontos.append(self._ponto_login())
        pontos.append(self._ponto_senha_errada())
        pontos.append(self._ponto_logout())
        pontos.append(self._ponto_perfil_fiscal())
        pontos.append(self._ponto_perfil_sem_login())
        return pontos

    def _cadastrar(self, ponto, acao: str):
        """POST de cadastro da conta descartável."""
        return self._chamar_http(
            ponto, self._nova_sessao(), "", "POST", "/api/v1/auth/register", acao,
            json_corpo={"email": self.email, "password": self.senha_descartavel, "full_name": "QA Novo Api"},
        )

    def _ponto_cadastro(self):
        """Cadastro cria comprador."""
        ponto = self._novo_ponto("Ponto 1 - Cadastro cria conta de comprador", HISTORIA_CADASTRO)
        resposta = self._cadastrar(ponto, "cadastro")
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        if resposta.status == 201 and corpo.get("email") == self.email and str(corpo.get("role")).lower() == "customer":
            ponto.concluir("VALIDO", "O cadastro responde 201 com o e-mail enviado e o papel `customer`.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "cadastro respondeu " + str(resposta.status) + " " + str(corpo)[:160])
        return ponto

    def _ponto_duplicado(self):
        """Mesmo e-mail é recusado com a mensagem certa."""
        ponto = self._novo_ponto("Ponto 2 - E-mail já cadastrado é recusado", HISTORIA_CADASTRO)
        resposta = self._cadastrar(ponto, "cadastro-duplicado")
        if resposta.status == 409 and "E-mail já cadastrado" in self._detalhe(resposta):
            ponto.concluir("VALIDO", "O segundo cadastro com o mesmo e-mail responde 409 \"E-mail já cadastrado\".")
        else:
            ponto.concluir("FALHA DE PRODUTO", "duplicado respondeu " + str(resposta.status) + " " + self._detalhe(resposta))
        return ponto

    def _entrar(self, ponto, senha: str, acao: str):
        """POST do formulário OAuth2 de login."""
        return self._chamar_http(
            ponto, self._nova_sessao(), self.email, "POST", "/api/v1/auth/token", acao,
            formulario={"username": self.email, "password": senha},
        )

    def _ponto_login(self):
        """Senha correta devolve os dois tokens."""
        ponto = self._novo_ponto("Ponto 3 - Login com senha correta devolve os tokens", HISTORIA_LOGIN)
        resposta = self._entrar(ponto, self.senha_descartavel, "login-correto")
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        if resposta.status == 200 and corpo.get("access_token") and corpo.get("refresh_token"):
            self.token = str(corpo["access_token"])
            ponto.concluir("VALIDO", "O login responde 200 com `access_token` e `refresh_token` (mascarados na evidência).")
        else:
            ponto.concluir("FALHA DE PRODUTO", "login respondeu " + str(resposta.status) + " " + self._detalhe(resposta))
        return ponto

    def _ponto_senha_errada(self):
        """Senha errada é recusada."""
        ponto = self._novo_ponto("Ponto 4 - Senha errada é recusada", HISTORIA_LOGIN)
        resposta = self._entrar(ponto, "senha-errada-" + self._marca, "login-senha-errada")
        if resposta.status == 401 and "Credenciais inválidas" in self._detalhe(resposta):
            ponto.concluir("VALIDO", "A senha errada responde 401 \"Credenciais inválidas\".")
        else:
            ponto.concluir("FALHA DE PRODUTO", "senha errada respondeu " + str(resposta.status) + " " + self._detalhe(resposta))
        return ponto

    def _ponto_logout(self):
        """O mesmo token vale antes e deixa de valer depois do logout."""
        ponto = self._novo_ponto("Ponto 5 - Token do logout deixa de valer", HISTORIA_LOGIN)
        if not self.token:
            ponto.concluir("EVIDENCIA INVALIDA", "sem token do Ponto 3 não há o que revogar")
            return ponto
        http = self._sessao_com_token(self.token)
        antes = self._chamar_http(ponto, http, self.email, "GET", "/api/v1/auth/me", "me-antes-do-logout")
        saida = self._chamar_http(ponto, http, self.email, "POST", "/api/v1/auth/logout", "logout")
        depois = self._chamar_http(ponto, http, self.email, "GET", "/api/v1/auth/me", "me-depois-do-logout")
        corpo = antes.corpo if isinstance(antes.corpo, dict) else {}
        if antes.status == 200 and corpo.get("email") == self.email and saida.status < 300 and depois.status == 401:
            ponto.concluir("VALIDO", "O `/me` responde 200 antes do logout e 401 com o mesmo token depois.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "antes " + str(antes.status) + ", logout " + str(saida.status)
                           + ", depois " + str(depois.status))
        return ponto

    def _ponto_perfil_fiscal(self):
        """O corpo que a tela `#/conta` monta é aceito."""
        ponto = self._novo_ponto("Ponto 6 - Perfil fiscal enviado como a tela envia é salvo", HISTORIA_PERFIL)
        corpo_da_tela = {
            "person_type": "individual",
            "legal_name": "QA Cliente",
            "document": "529.982.247-25",
            "address_line": "Rua do Teste, 100",
            "city": "São Paulo",
            "state": "SP",
            "postal_code": "01001-000",
            "country": "BR",
        }
        resposta = self._chamar(ponto, "cliente", "PUT", "/api/v1/billing/profile", "perfil-fiscal-da-tela",
                                corpo_json=corpo_da_tela)
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        if resposta.status == 200 and corpo.get("legal_name") == "QA Cliente":
            ponto.concluir("VALIDO", "O perfil fiscal com o corpo da tela é salvo (200).")
        else:
            ponto.concluir("FALHA DE PRODUTO", "ao corpo que a tela envia (`person_type` \"individual\") a API respondeu "
                           + str(resposta.status) + " " + str(resposta.corpo)[:200])
        return ponto

    def _ponto_perfil_sem_login(self):
        """Sem sessão não há perfil fiscal."""
        ponto = self._novo_ponto("Ponto 7 - Perfil fiscal sem login é recusado", HISTORIA_PERFIL)
        resposta = self._chamar(ponto, "visitante", "PUT", "/api/v1/billing/profile", "perfil-fiscal-sem-login",
                                corpo_json={"legal_name": "x", "document": "x"})
        if resposta.status == 401:
            ponto.concluir("VALIDO", "Sem sessão o perfil fiscal responde 401.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "sem sessão respondeu " + str(resposta.status))
        return ponto
