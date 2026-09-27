"""Suíte de integração — domínio compra (carrinho, simulador, convidado, cupom, webhook).

Implementa os pontos de `.spec/test/planos/compra.yaml`.
"""

import re

from testes.api.base import SuiteDoEseller

HISTORIA_CARRINHO = "História 1 - Comprador compra pelo carrinho e paga"
HISTORIA_CONVIDADO = "História 2 - Visitante compra um e-book sem ter conta"
HISTORIA_CUPOM = "História 3 - Comprador usa um cupom de desconto"
HISTORIA_PEDIDOS = "História 4 - Comprador acompanha os pedidos e retoma um pagamento pendente"
HISTORIA_WEBHOOK = "História 5 - Sistema confirma o pagamento pelo webhook"
PADRAO_CSRF = re.compile(r'name="csrf_token" value="([^"]+)"')
TEXTO_PAGO = "✓ Pago"
TEXTO_BAIXAR = "Baixar"


class SuiteCompra(SuiteDoEseller):
    """Fluxo de valor da loja: do carrinho ao pedido pago, com cupom e webhook."""

    dominio = "compra"

    def __init__(self, config, adaptador, registrador) -> None:
        """Guarda as referências que um ponto passa ao seguinte."""
        super().__init__(config, adaptador, registrador)
        self.referencia_do_carrinho = ""
        self.referencia_do_convidado = ""
        self.links_depois_do_primeiro_webhook = -1

    def executar(self) -> list:
        """Executa os pontos na ordem do plano."""
        pontos = []
        pontos.append(self._ponto_carrinho())
        pontos.append(self._ponto_finalizar())
        pontos.append(self._ponto_simulador())
        pontos.append(self._ponto_visual_do_pagamento())
        pontos.append(self._ponto_biblioteca_depois_de_pago())
        pontos.append(self._ponto_convidado())
        pontos.append(self._ponto_cupom_valido())
        pontos.append(self._ponto_cupom_inexistente())
        pontos.append(self._ponto_pedido_com_cupom())
        pontos.append(self._ponto_cupom_minusculo())
        pontos.append(self._ponto_retomar_pendente())
        pontos.append(self._ponto_webhook_aprovado())
        pontos.append(self._ponto_webhook_repetido())
        pontos.append(self._ponto_pendente_sem_download())
        return pontos

    # ── carrinho e simulador ─────────────────────────────────────────────

    def _ponto_carrinho(self):
        """Adicionar e ver o item no carrinho."""
        ponto = self._novo_ponto("Ponto 1 - Carrinho recebe o e-book e mostra o preço", HISTORIA_CARRINHO)
        adicao = self._chamar(ponto, "cliente", "POST", "/api/v1/cart/fastapi-do-zero", "carrinho-adicionar")
        lista = self._chamar(ponto, "cliente", "GET", "/api/v1/cart", "carrinho-listar")
        itens = lista.corpo if isinstance(lista.corpo, list) else []
        for item in itens:
            if item.get("slug") == "fastapi-do-zero" and item.get("price") == "49.90":
                ponto.concluir("VALIDO", "O carrinho lista `fastapi-do-zero` a 49.90 depois da adição (" + str(adicao.status) + ").")
                return ponto
        ponto.concluir("FALHA DE PRODUTO", "adição " + str(adicao.status) + "; carrinho: " + ", ".join(self._slugs(itens)))
        return ponto

    def _ponto_finalizar(self):
        """Checkout do carrinho cria pedido pendente."""
        ponto = self._novo_ponto("Ponto 2 - Finalizar o carrinho cria pedido pendente com link de pagamento", HISTORIA_CARRINHO)
        resposta = self._chamar(ponto, "cliente", "POST", "/api/v1/cart/checkout", "carrinho-finalizar", corpo_json={})
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        if resposta.status < 300 and corpo.get("reference") and corpo.get("status") == "pending" and corpo.get("amount") == "49.90":
            self.referencia_do_carrinho = str(corpo["reference"])
            ponto.concluir("VALIDO", "O checkout cria o pedido pendente de 49.90 com referência própria.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "checkout respondeu " + str(resposta.status) + " " + str(corpo)[:160])
        return ponto

    def _pagar_no_simulador(self, ponto, referencia: str, prefixo: str):
        """Abre o simulador, lê o csrf_token e aprova; devolve a resposta do confirm."""
        http = self._nova_sessao()
        pagina = self._chamar_http(ponto, http, "", "GET", "/pay/simulate/" + referencia, prefixo + "-simulador",
                                   procurar=["Simulador de pagamento", "Aprovar pagamento"])
        encontrado = PADRAO_CSRF.search(pagina.texto)
        if not encontrado:
            return pagina, None
        self._segredo(encontrado.group(1))
        confirmacao = self._chamar_http(
            ponto, http, "", "POST", "/pay/confirm/" + referencia, prefixo + "-aprovar",
            formulario={"decision": "approved", "csrf_token": encontrado.group(1)},
        )
        return pagina, confirmacao

    def _ponto_simulador(self):
        """Aprovar no simulador leva ao pedido pago com download."""
        ponto = self._novo_ponto("Ponto 3 - Aprovar no simulador deixa o pedido pago com download", HISTORIA_CARRINHO)
        if not self.referencia_do_carrinho:
            ponto.concluir("EVIDENCIA INVALIDA", "sem o pedido do Ponto 2 não há o que pagar")
            return ponto
        pagina, confirmacao = self._pagar_no_simulador(ponto, self.referencia_do_carrinho, "carrinho")
        if confirmacao is None:
            ponto.concluir("FALHA DE PRODUTO", "o simulador respondeu " + str(pagina.status) + " sem formulário de aprovação")
            return ponto
        destino = self._cabecalho(confirmacao, "location")
        pedido = self._chamar(ponto, "visitante", "GET", "/pedido/" + self.referencia_do_carrinho, "carrinho-pedido-pago",
                              procurar=[TEXTO_PAGO, TEXTO_BAIXAR])
        if confirmacao.status in (302, 303) and destino.endswith("/pedido/" + self.referencia_do_carrinho) \
                and TEXTO_PAGO in pedido.texto and TEXTO_BAIXAR in pedido.texto:
            ponto.concluir("VALIDO", "O confirm redireciona para o pedido, que mostra \"✓ Pago\" e \"Baixar\".")
        else:
            ponto.concluir("FALHA DE PRODUTO", "confirm " + str(confirmacao.status) + " → " + destino
                           + "; página do pedido sem \"✓ Pago\"/\"Baixar\"")
        return ponto

    def _ponto_visual_do_pagamento(self):
        """A folha de estilo das páginas de pagamento chega como CSS."""
        ponto = self._novo_ponto("Ponto 4 - Páginas de pagamento recebem o visual da loja", HISTORIA_CARRINHO)
        resposta = self._chamar(ponto, "visitante", "GET", "/static/css/design-system.css", "estilo-das-paginas-de-pagamento")
        tipo = self._cabecalho(resposta, "content-type")
        if resposta.status == 200 and "text/css" in tipo:
            ponto.concluir("VALIDO", "A folha de estilo do simulador e do pedido chega como `text/css`.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "`/static/css/design-system.css` pelo endereço da loja veio como `"
                           + tipo + "` (status " + str(resposta.status) + "): simulador e pedido aparecem sem estilo")
        return ponto

    def _ponto_biblioteca_depois_de_pago(self):
        """O e-book pago entra na biblioteca."""
        ponto = self._novo_ponto("Ponto 5 - E-book pago entra na biblioteca do comprador", HISTORIA_CARRINHO)
        resposta = self._chamar(ponto, "cliente", "GET", "/api/v1/library", "biblioteca-depois-de-pago")
        if "fastapi-do-zero" in self._slugs(resposta.corpo):
            ponto.concluir("VALIDO", "A biblioteca do cliente passa a conter `fastapi-do-zero`.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "biblioteca: " + ", ".join(self._slugs(resposta.corpo)))
        return ponto

    # ── convidado e cupom ────────────────────────────────────────────────

    def _pedido_de_convidado(self, ponto, sufixo: str, acao: str, cupom: str = ""):
        """POST /orders sem sessão, com e-mail de QA."""
        corpo = {"product_slug": "python-na-pratica",
                 "buyer_email": "qa-convidado-" + sufixo + "-" + self._marca + "@eseller-qa.test"}
        if cupom:
            corpo["coupon_code"] = cupom
        return self._chamar(ponto, "visitante", "POST", "/api/v1/orders", acao, corpo_json=corpo)

    def _ponto_convidado(self):
        """Convidado cria pedido com link de pagamento."""
        ponto = self._novo_ponto("Ponto 6 - Convidado cria pedido pendente com link de pagamento", HISTORIA_CONVIDADO)
        resposta = self._pedido_de_convidado(ponto, "a", "pedido-convidado")
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        referencia = str(corpo.get("reference", ""))
        if resposta.status == 201 and corpo.get("status") == "pending" and \
                str(corpo.get("checkout_url", "")).endswith("/pay/simulate/" + referencia):
            self.referencia_do_convidado = referencia
            ponto.concluir("VALIDO", "O pedido de convidado nasce pendente com `checkout_url` para o simulador.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "pedido de convidado respondeu " + str(resposta.status) + " " + str(corpo)[:160])
        return ponto

    def _validar_cupom(self, ponto, codigo: str, acao: str):
        """POST /coupons/validate sobre 39.90."""
        return self._chamar(ponto, "visitante", "POST", "/api/v1/coupons/validate", acao,
                            corpo_json={"code": codigo, "amount": "39.90"})

    def _ponto_cupom_valido(self):
        """BEMVINDO10 dá 35.91."""
        ponto = self._novo_ponto("Ponto 7 - Cupom válido calcula o total com desconto", HISTORIA_CUPOM)
        resposta = self._validar_cupom(ponto, "BEMVINDO10", "cupom-valido")
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        if corpo.get("valid") is True and corpo.get("total") == "35.91":
            ponto.concluir("VALIDO", "BEMVINDO10 sobre 39.90 é válido com total 35.91.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "validação respondeu " + str(resposta.status) + " " + str(corpo))
        return ponto

    def _ponto_cupom_inexistente(self):
        """Cupom inexistente é recusado."""
        ponto = self._novo_ponto("Ponto 8 - Cupom inexistente é recusado", HISTORIA_CUPOM)
        resposta = self._validar_cupom(ponto, "QA-NAO-EXISTE", "cupom-inexistente")
        if 400 <= resposta.status < 500 and "inválido" in self._detalhe(resposta).lower():
            ponto.concluir("VALIDO", "Cupom inexistente responde " + str(resposta.status) + " \"" + self._detalhe(resposta) + "\".")
        else:
            ponto.concluir("FALHA DE PRODUTO", "cupom inexistente respondeu " + str(resposta.status) + " " + self._detalhe(resposta))
        return ponto

    def _ponto_pedido_com_cupom(self):
        """Pedido grava o valor com desconto."""
        ponto = self._novo_ponto("Ponto 9 - Pedido com cupom é gravado com o desconto", HISTORIA_CUPOM)
        resposta = self._pedido_de_convidado(ponto, "cupom", "pedido-com-cupom", "BEMVINDO10")
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        if resposta.status == 201 and corpo.get("amount") == "35.91":
            ponto.concluir("VALIDO", "O pedido com BEMVINDO10 é gravado com `amount` 35.91.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "pedido com cupom respondeu " + str(resposta.status) + " " + str(corpo)[:160])
        return ponto

    def _ponto_cupom_minusculo(self):
        """A prévia aceita minúsculas (põe em maiúsculas); o pedido precisa aceitar igual."""
        ponto = self._novo_ponto("Ponto 10 - Cupom digitado em minúsculas vale no pedido como vale na prévia", HISTORIA_CUPOM)
        previa = self._validar_cupom(ponto, "BEMVINDO10", "cupom-previa-da-tela")
        pedido = self._pedido_de_convidado(ponto, "minusculo", "pedido-cupom-minusculo", "bemvindo10")
        corpo = pedido.corpo if isinstance(pedido.corpo, dict) else {}
        previa_valida = isinstance(previa.corpo, dict) and previa.corpo.get("valid") is True
        if previa_valida and pedido.status == 201 and corpo.get("amount") == "35.91":
            ponto.concluir("VALIDO", "Digitado em minúsculas, o cupom vale no pedido como vale na prévia (35.91).")
        else:
            ponto.concluir("FALHA DE PRODUTO", "a prévia diz válido, mas o pedido com `bemvindo10` respondeu "
                           + str(pedido.status) + " " + str(corpo)[:160])
        return ponto

    # ── pedidos e webhook ────────────────────────────────────────────────

    def _ponto_retomar_pendente(self):
        """Meus pedidos oferece como pagar o pendente (RF-25)."""
        ponto = self._novo_ponto("Ponto 11 - Pedido pendente em Meus pedidos traz como pagar", HISTORIA_PEDIDOS)
        criado = self._chamar(ponto, "sem_compras", "POST", "/api/v1/orders", "pedido-pendente-da-conta",
                              corpo_json={"product_slug": "python-na-pratica", "buyer_email": self._conta("sem_compras")})
        lista = self._chamar(ponto, "sem_compras", "GET", "/api/v1/orders/my", "meus-pedidos")
        referencia = str(criado.corpo.get("reference", "")) if isinstance(criado.corpo, dict) else ""
        pedidos = lista.corpo if isinstance(lista.corpo, list) else []
        for pedido in pedidos:
            if pedido.get("reference") == referencia:
                if pedido.get("status") == "pending" and pedido.get("amount") and pedido.get("checkout_url"):
                    ponto.concluir("VALIDO", "O pedido pendente aparece com status, valor e `checkout_url` para pagar.")
                else:
                    ponto.concluir("FALHA DE PRODUTO", "o pedido pendente aparece com `checkout_url` "
                                   + str(pedido.get("checkout_url")) + ": a tela não tem como oferecer \"Pagar\"")
                return ponto
        ponto.concluir("FALHA DE PRODUTO", "o pedido criado (" + str(criado.status) + ") não aparece em Meus pedidos")
        return ponto

    def _webhook(self, ponto, referencia: str, acao: str):
        """Webhook de pagamento aprovado (provedor fake)."""
        return self._chamar(ponto, "visitante", "POST", "/api/v1/webhooks/mercadopago", acao,
                            corpo_json={"provider_payment_id": "qa-webhook-" + referencia,
                                        "order_reference": referencia, "provider_status": "approved"})

    def _ponto_webhook_aprovado(self):
        """Webhook aprovado paga o pedido do convidado."""
        ponto = self._novo_ponto("Ponto 12 - Webhook aprovado paga o pedido", HISTORIA_WEBHOOK)
        if not self.referencia_do_convidado:
            ponto.concluir("EVIDENCIA INVALIDA", "sem o pedido do Ponto 6 não há o que pagar")
            return ponto
        resposta = self._webhook(ponto, self.referencia_do_convidado, "webhook-aprovado")
        pedido = self._chamar(ponto, "visitante", "GET", "/pedido/" + self.referencia_do_convidado, "webhook-pedido-pago",
                              procurar=[TEXTO_PAGO, TEXTO_BAIXAR])
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        self.links_depois_do_primeiro_webhook = pedido.texto.count("/api/v1/download/")
        if corpo.get("outcome") == "APPLIED" and TEXTO_PAGO in pedido.texto and TEXTO_BAIXAR in pedido.texto:
            ponto.concluir("VALIDO", "O webhook é aplicado e a página do pedido mostra \"✓ Pago\" com \"Baixar\".")
        else:
            ponto.concluir("FALHA DE PRODUTO", "webhook " + str(resposta.status) + " " + str(corpo)[:120])
        return ponto

    def _ponto_webhook_repetido(self):
        """O mesmo webhook não repete efeito."""
        ponto = self._novo_ponto("Ponto 13 - Webhook repetido não repete efeito", HISTORIA_WEBHOOK)
        if self.links_depois_do_primeiro_webhook < 0:
            ponto.concluir("EVIDENCIA INVALIDA", "sem o Ponto 12 não há webhook para repetir")
            return ponto
        resposta = self._webhook(ponto, self.referencia_do_convidado, "webhook-repetido")
        pedido = self._chamar(ponto, "visitante", "GET", "/pedido/" + self.referencia_do_convidado, "webhook-pedido-depois-da-repeticao",
                              procurar=["/api/v1/download/"])
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        links = pedido.texto.count("/api/v1/download/")
        if corpo.get("outcome") == "ALREADY_PROCESSED" and links == self.links_depois_do_primeiro_webhook:
            ponto.concluir("VALIDO", "A repetição volta ALREADY_PROCESSED e o pedido mantém " + str(links) + " link(s) de download.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "repetição: " + str(corpo)[:120] + "; links " + str(self.links_depois_do_primeiro_webhook)
                           + " → " + str(links))
        return ponto

    def _ponto_pendente_sem_download(self):
        """Pedido pendente não mostra download."""
        ponto = self._novo_ponto("Ponto 14 - Pedido pendente não libera download", HISTORIA_WEBHOOK)
        criado = self._pedido_de_convidado(ponto, "pendente", "pedido-pendente-convidado")
        referencia = str(criado.corpo.get("reference", "")) if isinstance(criado.corpo, dict) else ""
        if not referencia:
            ponto.concluir("FALHA DE PRODUTO", "não foi possível criar o pedido (" + str(criado.status) + ")")
            return ponto
        pedido = self._chamar(ponto, "visitante", "GET", "/pedido/" + referencia, "pedido-pendente-pagina",
                              procurar=["Aguardando", "/api/v1/download/"])
        if "Aguardando" in pedido.texto and "/api/v1/download/" not in pedido.texto:
            ponto.concluir("VALIDO", "O pedido pendente mostra \"Aguardando\" e nenhum link de download.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "a página do pedido pendente libera download ou não mostra \"Aguardando\"")
        return ponto
