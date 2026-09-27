"""Suíte de integração — domínio biblioteca (posse, download, favoritos, avaliações).

Implementa os pontos de `.spec/test/planos/biblioteca.yaml`. Os tokens de download
vêm da massa (válido, expirado, esgotado) e são mascarados na evidência.
"""

from testes.api.base import SuiteDoEseller

HISTORIA_DOWNLOAD = "História 1 - Comprador baixa um e-book da biblioteca"
HISTORIA_FAVORITOS = "História 2 - Comprador guarda e-books nos favoritos"
HISTORIA_AVALIACAO = "História 3 - Comprador avalia um e-book que comprou"


class SuiteBiblioteca(SuiteDoEseller):
    """Posse e entrega segura do e-book, favoritos e avaliação de comprador verificado."""

    dominio = "biblioteca"

    def __init__(self, config, adaptador, registrador) -> None:
        """Comentário único da avaliação desta execução."""
        super().__init__(config, adaptador, registrador)
        self.comentario = "qa-avaliacao-api-" + self._marca

    def executar(self) -> list:
        """Executa os pontos na ordem do plano."""
        pontos = []
        pontos.append(self._ponto_biblioteca_do_cliente())
        pontos.append(self._ponto_biblioteca_vazia())
        pontos.append(self._ponto_download_valido())
        pontos.append(self._ponto_download_negado(
            "Ponto 4 - Link expirado é negado", "download_expirado", "download-expirado", (410,), "expirado"))
        pontos.append(self._ponto_download_negado(
            "Ponto 5 - Link que atingiu o limite é negado", "download_esgotado", "download-esgotado",
            (403, 410, 429), "limite"))
        pontos.append(self._ponto_link_so_para_dono())
        pontos.append(self._ponto_favoritos())
        pontos.append(self._ponto_avaliacao())
        pontos.append(self._ponto_avaliacao_recusada())
        pontos.append(self._ponto_avaliacao_pendente_oculta())
        return pontos

    def _ponto_biblioteca_do_cliente(self):
        """Os dois e-books pagos estão na biblioteca."""
        ponto = self._novo_ponto("Ponto 1 - Biblioteca do comprador traz os e-books pagos", HISTORIA_DOWNLOAD)
        resposta = self._chamar(ponto, "cliente", "GET", "/api/v1/library", "biblioteca-cliente")
        slugs = self._slugs(resposta.corpo)
        if "python-na-pratica" in slugs and "arquitetura-limpa-web" in slugs:
            ponto.concluir("VALIDO", "A biblioteca do cliente traz `python-na-pratica` e `arquitetura-limpa-web`.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "biblioteca do cliente: " + ", ".join(slugs))
        return ponto

    def _ponto_biblioteca_vazia(self):
        """Contraste: quem não comprou tem biblioteca vazia."""
        ponto = self._novo_ponto("Ponto 2 - Biblioteca de quem não comprou está vazia", HISTORIA_DOWNLOAD)
        resposta = self._chamar(ponto, "sem_compras", "GET", "/api/v1/library", "biblioteca-sem-compras")
        if resposta.status == 200 and resposta.corpo == []:
            ponto.concluir("VALIDO", "A biblioteca de `sem_compras` é uma lista vazia.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "biblioteca de sem_compras: " + str(resposta.status) + " " + ", ".join(self._slugs(resposta.corpo)))
        return ponto

    def _baixar(self, ponto, nome_do_token: str, acao: str, procurar: list = None):
        """GET do link de download da massa (token mascarado na evidência)."""
        token = self._segredo(self._adaptador.token_da_massa(nome_do_token))
        return self._chamar_http(ponto, self._nova_sessao(), "", "GET", "/api/v1/download/" + token, acao,
                                 procurar=procurar)

    def _ponto_download_valido(self):
        """Link válido entrega o arquivo como anexo, sem caminho do servidor."""
        ponto = self._novo_ponto("Ponto 3 - Link válido entrega o arquivo sem expor o caminho", HISTORIA_DOWNLOAD)
        resposta = self._baixar(ponto, "download_valido", "download-valido",
                                procurar=["Python na Prática", "/app/storage", "storage/ebooks"])
        disposicao = self._cabecalho(resposta, "content-disposition")
        expoe_caminho = "/app/storage" in resposta.texto or "storage/ebooks" in resposta.texto
        if resposta.status == 200 and "attachment" in disposicao and "Python na Pr" in resposta.texto and not expoe_caminho:
            ponto.concluir("VALIDO", "O link válido entrega o arquivo como anexo, com o texto do e-book e sem caminho do servidor.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "download válido: status " + str(resposta.status) + ", disposição `" + disposicao + "`")
        return ponto

    def _ponto_download_negado(self, nome: str, nome_do_token: str, acao: str, status_aceitos: tuple, palavra: str):
        """Link expirado ou esgotado não entrega arquivo."""
        ponto = self._novo_ponto(nome, HISTORIA_DOWNLOAD)
        resposta = self._baixar(ponto, nome_do_token, acao)
        detalhe = self._detalhe(resposta).lower()
        if resposta.status in status_aceitos and palavra in detalhe:
            ponto.concluir("VALIDO", "O link responde " + str(resposta.status) + " \"" + self._detalhe(resposta) + "\" sem arquivo.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "esperava recusa (" + str(status_aceitos) + ", \"" + palavra + "\"); veio "
                           + str(resposta.status) + " " + self._detalhe(resposta))
        return ponto

    def _ponto_link_so_para_dono(self):
        """Quem não possui é recusado; o dono recebe link."""
        ponto = self._novo_ponto("Ponto 6 - Quem não possui o e-book não gera link", HISTORIA_DOWNLOAD)
        estranho = self._chamar(ponto, "sem_compras", "POST", "/api/v1/library/python-na-pratica/download-link",
                                "link-de-quem-nao-possui")
        dono = self._chamar(ponto, "cliente", "POST", "/api/v1/library/python-na-pratica/download-link",
                            "link-do-dono")
        url_do_dono = str(dono.corpo.get("url", "")) if isinstance(dono.corpo, dict) else ""
        if 400 <= estranho.status < 500 and dono.status < 300 and "/api/v1/download/" in url_do_dono:
            ponto.concluir("VALIDO", "Quem não possui recebe " + str(estranho.status) + "; o dono recebe um link de download.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "sem posse " + str(estranho.status) + ", dono " + str(dono.status))
        return ponto

    def _ponto_favoritos(self):
        """Favoritar e ver na lista."""
        ponto = self._novo_ponto("Ponto 7 - Favorito entra na lista de favoritos", HISTORIA_FAVORITOS)
        adicao = self._chamar(ponto, "cliente", "POST", "/api/v1/wishlist/fastapi-do-zero", "favoritar")
        lista = self._chamar(ponto, "cliente", "GET", "/api/v1/wishlist", "favoritos")
        if "fastapi-do-zero" in self._slugs(lista.corpo):
            ponto.concluir("VALIDO", "Depois de favoritar (" + str(adicao.status) + "), `fastapi-do-zero` está nos favoritos.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "favoritar " + str(adicao.status) + "; lista: " + ", ".join(self._slugs(lista.corpo)))
        return ponto

    def _avaliar(self, ponto, perfil: str, acao: str):
        """POST de avaliação em python-na-pratica."""
        return self._chamar(ponto, perfil, "POST", "/api/v1/products/python-na-pratica/reviews", acao,
                            corpo_json={"rating": 5, "comment": self.comentario})

    def _ponto_avaliacao(self):
        """Dono avalia: a avaliação é criada (a pendência é provada no Ponto 10)."""
        ponto = self._novo_ponto("Ponto 8 - Comprador verificado envia avaliação", HISTORIA_AVALIACAO)
        resposta = self._avaliar(ponto, "cliente", "avaliacao-do-dono")
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        if resposta.status == 201 and corpo.get("id") and corpo.get("comment") == self.comentario:
            ponto.concluir("VALIDO", "A avaliação do dono é criada (201) com o comentário enviado.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "avaliação do dono respondeu " + str(resposta.status) + " " + str(corpo)[:160])
        return ponto

    def _ponto_avaliacao_recusada(self):
        """Quem não comprou é recusado."""
        ponto = self._novo_ponto("Ponto 9 - Quem não comprou não avalia", HISTORIA_AVALIACAO)
        resposta = self._avaliar(ponto, "sem_compras", "avaliacao-sem-posse")
        if resposta.status == 403 and "Só quem comprou pode avaliar" in self._detalhe(resposta):
            ponto.concluir("VALIDO", "Sem posse, a avaliação responde 403 \"Só quem comprou pode avaliar\".")
        else:
            ponto.concluir("FALHA DE PRODUTO", "sem posse respondeu " + str(resposta.status) + " " + self._detalhe(resposta))
        return ponto

    def _ponto_avaliacao_pendente_oculta(self):
        """A pendente não aparece na lista pública."""
        ponto = self._novo_ponto("Ponto 10 - Avaliação pendente não aparece para o público", HISTORIA_AVALIACAO)
        resposta = self._chamar(ponto, "visitante", "GET", "/api/v1/products/python-na-pratica/reviews",
                                "avaliacoes-publicas", procurar=[self.comentario])
        if resposta.status == 200 and self.comentario not in resposta.texto:
            ponto.concluir("VALIDO", "A lista pública de avaliações não contém o comentário pendente.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "a avaliação pendente aparece para o público (status " + str(resposta.status) + ")")
        return ponto
