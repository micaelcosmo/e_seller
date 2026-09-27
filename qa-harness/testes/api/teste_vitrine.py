"""Suíte de integração — domínio vitrine.

Implementa os pontos de `.spec/test/planos/vitrine.yaml`.
"""

from testes.api.base import SuiteDoEseller

HISTORIA_CATALOGO = "História 1 - Visitante conhece a loja e o catálogo"
HISTORIA_BUSCA = "História 2 - Visitante busca um e-book por título ou autor"
HISTORIA_FILTRO = "História 3 - Visitante filtra e ordena o catálogo por preço"
HISTORIA_DETALHE = "História 4 - Visitante vê o detalhe de um e-book"
HISTORIA_NEWSLETTER = "História 5 - Visitante assina a newsletter"
HISTORIA_INSTITUCIONAL = "História 6 - Visitante lê a política de privacidade e os termos"
PUBLICADOS = ["python-na-pratica", "fastapi-do-zero", "arquitetura-limpa-web"]


class SuiteVitrine(SuiteDoEseller):
    """Catálogo, busca, filtro, detalhe, newsletter e páginas institucionais."""

    dominio = "vitrine"

    def executar(self) -> list:
        """Executa os pontos na ordem do plano."""
        pontos = []
        pontos.append(self._ponto_catalogo())
        pontos.append(self._ponto_rascunho())
        pontos.append(self._ponto_busca())
        pontos.append(self._ponto_filtro_de_preco())
        pontos.append(self._ponto_ordenacao())
        pontos.append(self._ponto_detalhe())
        pontos.append(self._ponto_newsletter())
        pontos.append(self._ponto_institucional(
            "Ponto 8 - Endereço da política de privacidade entrega a política",
            "/privacidade", "Política de Privacidade", "privacidade"))
        pontos.append(self._ponto_institucional(
            "Ponto 9 - Endereço dos termos de uso entrega os termos",
            "/termos", "Termos de Uso", "termos"))
        return pontos

    def _ponto_catalogo(self):
        """Os três publicados, com título/autor/preço, sem o rascunho."""
        ponto = self._novo_ponto("Ponto 1 - Catálogo público lista os três publicados sem o rascunho", HISTORIA_CATALOGO)
        resposta = self._chamar(ponto, "visitante", "GET", "/api/v1/products", "catalogo-publico")
        slugs = self._slugs(resposta.corpo)
        if resposta.status != 200:
            ponto.concluir("FALHA DE PRODUTO", "o catálogo respondeu " + str(resposta.status))
            return ponto
        if "rascunho-oculto" in slugs:
            ponto.concluir("FALHA DE PRODUTO", "o rascunho `rascunho-oculto` aparece no catálogo público")
            return ponto
        faltando = []
        for slug in PUBLICADOS:
            if slug not in slugs:
                faltando.append(slug)
        if faltando or len(slugs) != 3:
            ponto.concluir("FALHA DE PRODUTO", "esperava os 3 publicados; veio " + ", ".join(slugs))
            return ponto
        for item in resposta.corpo:
            if not item.get("title") or not item.get("author") or not item.get("price"):
                ponto.concluir("FALHA DE PRODUTO", "item sem título, autor ou preço: " + str(item.get("slug")))
                return ponto
        ponto.concluir("VALIDO", "O catálogo lista exatamente os 3 publicados, cada um com título, autor e preço, e não mostra o rascunho.")
        return ponto

    def _ponto_rascunho(self):
        """Rascunho não abre por endereço direto."""
        ponto = self._novo_ponto("Ponto 2 - Rascunho não abre pelo endereço direto", HISTORIA_CATALOGO)
        resposta = self._chamar(ponto, "visitante", "GET", "/api/v1/products/rascunho-oculto", "rascunho-direto")
        if resposta.status == 404:
            ponto.concluir("VALIDO", "O endereço direto do rascunho responde 404: ele não existe para a vitrine.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "o rascunho respondeu " + str(resposta.status) + " em vez de 404")
        return ponto

    def _ponto_busca(self):
        """A busca do SPA (`q=`) acha o título certo e só ele."""
        ponto = self._novo_ponto("Ponto 3 - Busca por FastAPI traz só o e-book certo", HISTORIA_BUSCA)
        resposta = self._chamar(ponto, "visitante", "GET", "/api/v1/products?q=FastAPI", "busca-fastapi")
        if resposta.status != 200:
            ponto.concluir("FALHA DE PRODUTO", "a busca `GET /api/v1/products?q=FastAPI` respondeu "
                           + str(resposta.status) + " (" + self._detalhe(resposta) + ")")
            return ponto
        slugs = self._slugs(resposta.corpo)
        if "fastapi-do-zero" in slugs and "python-na-pratica" not in slugs:
            ponto.concluir("VALIDO", "A busca por FastAPI traz `fastapi-do-zero` e não traz `python-na-pratica`.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "a busca trouxe " + ", ".join(slugs))
        return ponto

    def _ponto_filtro_de_preco(self):
        """Filtro a partir de 50 reais."""
        ponto = self._novo_ponto("Ponto 4 - Filtro a partir de 50 reais traz só o e-book mais caro", HISTORIA_FILTRO)
        resposta = self._chamar(ponto, "visitante", "GET", "/api/v1/products?price_min=50", "filtro-preco-50")
        slugs = self._slugs(resposta.corpo)
        if resposta.status == 200 and slugs == ["arquitetura-limpa-web"]:
            ponto.concluir("VALIDO", "Com `price_min=50` só vem `arquitetura-limpa-web` (R$ 59,90).")
        else:
            ponto.concluir("FALHA DE PRODUTO", "status " + str(resposta.status) + "; veio " + ", ".join(slugs))
        return ponto

    def _ponto_ordenacao(self):
        """Ordenação crescente de preço."""
        ponto = self._novo_ponto("Ponto 5 - Ordenação por menor preço começa pelo mais barato", HISTORIA_FILTRO)
        resposta = self._chamar(ponto, "visitante", "GET", "/api/v1/products?sort=price_asc", "ordenacao-menor-preco")
        if resposta.status != 200 or not isinstance(resposta.corpo, list) or not resposta.corpo:
            ponto.concluir("FALHA DE PRODUTO", "a ordenação respondeu " + str(resposta.status))
            return ponto
        precos = []
        for item in resposta.corpo:
            precos.append(float(item["price"]))
        crescente = True
        indice = 1
        while indice < len(precos):
            if precos[indice] < precos[indice - 1]:
                crescente = False
            indice = indice + 1
        if resposta.corpo[0]["slug"] == "python-na-pratica" and crescente:
            ponto.concluir("VALIDO", "A lista começa por `python-na-pratica` (39,90) e os preços vêm em ordem crescente.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "ordem obtida: " + ", ".join(self._slugs(resposta.corpo)))
        return ponto

    def _ponto_detalhe(self):
        """Detalhe com os campos da US-02."""
        ponto = self._novo_ponto("Ponto 6 - Detalhe traz título, autor, descrição e preço", HISTORIA_DETALHE)
        resposta = self._chamar(ponto, "visitante", "GET", "/api/v1/products/python-na-pratica", "detalhe-python")
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        if (resposta.status == 200 and corpo.get("title") == "Python na Prática" and corpo.get("author")
                and corpo.get("description") and corpo.get("price") == "39.90"):
            ponto.concluir("VALIDO", "O detalhe traz título, autor, descrição e preço 39.90 de `python-na-pratica`.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "detalhe incompleto ou status " + str(resposta.status))
        return ponto

    def _ponto_newsletter(self):
        """Inscrição idempotente."""
        ponto = self._novo_ponto("Ponto 7 - Newsletter aceita a inscrição e a repetição sem duplicar", HISTORIA_NEWSLETTER)
        email = "qa-news-" + self._marca + "@eseller-qa.test"
        primeira = self._chamar(ponto, "visitante", "POST", "/api/v1/newsletter/subscribe", "newsletter-primeira",
                                corpo_json={"email": email})
        segunda = self._chamar(ponto, "visitante", "POST", "/api/v1/newsletter/subscribe", "newsletter-repetida",
                               corpo_json={"email": email})
        respostas = [primeira, segunda]
        for resposta in respostas:
            corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
            if resposta.status >= 300 or corpo.get("status") != "subscribed":
                ponto.concluir("FALHA DE PRODUTO", "inscrição respondeu " + str(resposta.status) + " " + str(corpo))
                return ponto
        ponto.concluir("VALIDO", "As duas inscrições do mesmo e-mail respondem sucesso com `status` subscribed.")
        return ponto

    def _ponto_institucional(self, nome: str, rota: str, titulo: str, acao: str):
        """O link do rodapé entrega a página institucional, não a loja."""
        ponto = self._novo_ponto(nome, HISTORIA_INSTITUCIONAL)
        resposta = self._chamar(ponto, "visitante", "GET", rota, acao, procurar=[titulo, "sua loja de e-books"])
        if resposta.status == 200 and titulo in resposta.texto:
            ponto.concluir("VALIDO", "O endereço `" + rota + "` entrega a página com o título \"" + titulo + "\".")
        else:
            ponto.concluir("FALHA DE PRODUTO", "`" + rota + "` pelo endereço da loja não entrega \"" + titulo
                           + "\" (status " + str(resposta.status) + "; veio a página da loja)")
        return ponto
