"""Suíte de integração — domínio exemplo.

Implementa os pontos de spec/test/planos/exemplo.yaml.
"""

from motor.suite import SuiteDeIntegracao


class SuiteExemplo(SuiteDeIntegracao):
    """Um ponto de exemplo: a evidência precisa mostrar o dado, não só o status."""

    dominio = "exemplo"

    def executar(self) -> list:
        pontos = []
        pontos.append(self._ponto_home_publica())
        return pontos

    def _ponto_home_publica(self):
        ponto = self._novo_ponto(
            "Ponto 1 - Home abre para quem não tem conta",
            "História 1 - Visitante conhece o produto",
        )
        resposta = self._chamar(ponto, "visitante", "GET", "/", "home-sem-sessao")
        if resposta.status != 200:
            ponto.concluir("FALHA DE PRODUTO", "a home respondeu " + str(resposta.status))
            return ponto
        if self._config.assinatura_da_aplicacao not in resposta.texto:
            ponto.concluir("EVIDENCIA INVALIDA", "200 sem a assinatura da aplicação: não prova que é a home certa")
            return ponto
        ponto.concluir("VALIDO", "A home responde 200 sem sessão e traz a assinatura da aplicação.")
        return ponto
