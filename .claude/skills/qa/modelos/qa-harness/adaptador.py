"""Adaptador deste projeto para o motor agnóstico da skill /qa.

O motor sabe executar suítes, jornadas, base visual, relatório e PDF; não sabe
como este projeto autentica, semeia dados ou quais suítes de API existem. Isso
é respondido aqui. Sobrescreva só o que precisar — o resto é o padrão de
`motor.adaptador.AdaptadorBase`.
"""

import requests

from motor.adaptador import AdaptadorBase, SessaoDoPerfil


class Adaptador(AdaptadorBase):
    """Autenticação, massa de dados, verificações e suítes deste projeto."""

    def verificar_ambiente(self) -> list:
        """Impedimentos além dos que o motor já confere (app no ar, navegador)."""
        impedimentos = []
        for perfil in self.config.perfis_com_conta():
            try:
                self.sessao(perfil)
            except Exception as erro:
                impedimentos.append("conta do perfil '" + perfil + "' não autentica: " + str(erro)[:160])
        return impedimentos

    def preparar_massa(self) -> bool:
        """Recoloca o banco no estado conhecido antes das suítes."""
        return True

    def autenticar(self, perfil: str) -> SessaoDoPerfil:
        """Exemplo com login por formulário JSON; troque pelo mecanismo real."""
        conta = self.config.perfil(perfil)["conta"]
        http = requests.Session()
        resposta = http.post(
            self.config.url_api + "/login",
            json={"email": conta, "senha": self.config.env.get("QA_SENHA", "")},
            timeout=30,
        )
        if resposta.status_code != 200:
            raise RuntimeError("login de " + conta + " respondeu " + str(resposta.status_code))
        return SessaoDoPerfil(perfil, conta, http)

    def suites_de_integracao(self) -> list:
        """Classes de `qa-harness/testes/api/`, na ordem de execução."""
        from testes.api.teste_exemplo import SuiteExemplo

        return [SuiteExemplo]
