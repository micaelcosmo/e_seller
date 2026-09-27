"""Suíte de integração — domínio administração (acesso, catálogo, vendas, moderação, cupons).

Implementa os pontos de `.spec/test/planos/administracao.yaml`.
"""

import re
from datetime import datetime, timedelta, timezone

from testes.api.base import SuiteDoEseller

HISTORIA_ACESSO = "História 1 - Administrador entra no painel administrativo"
HISTORIA_CADASTRO = "História 2 - Administrador cadastra e publica um e-book"
HISTORIA_VENDAS = "História 3 - Administrador acompanha as vendas"
HISTORIA_MODERACAO = "História 4 - Administrador modera as avaliações"
HISTORIA_CUPONS = "História 5 - Administrador gerencia cupons de desconto"
COMENTARIO_PENDENTE = "qa-avaliacao-pendente"
CONTEUDO_SENTINELA = "qa-conteudo-do-ebook"
PADRAO_LINK_DE_DOWNLOAD = re.compile(r"/api/v1/download/([A-Za-z0-9_\-]{16,})")


class SuiteAdministracao(SuiteDoEseller):
    """O que o administrador faz: entrar, cadastrar, acompanhar, moderar e promover."""

    dominio = "administracao"

    def __init__(self, config, adaptador, registrador) -> None:
        """Nomes únicos desta execução (e-book e cupom de QA)."""
        super().__init__(config, adaptador, registrador)
        self.titulo = "QA E-book " + self._marca
        self.slug = ""
        self.cupom = "QA-" + self._marca

    def executar(self) -> list:
        """Executa os pontos na ordem do plano."""
        pontos = []
        pontos.append(self._ponto_recusa("Ponto 1 - Comprador não acessa a administração", "cliente", 403, "admin-como-comprador"))
        pontos.append(self._ponto_recusa("Ponto 2 - Sem login a administração recusa", "visitante", 401, "admin-sem-login"))
        pontos.append(self._ponto_login_do_painel())
        pontos.append(self._ponto_cadastro())
        pontos.append(self._ponto_arquivo_exe())
        pontos.append(self._ponto_publicar())
        pontos.append(self._ponto_lista_de_pedidos())
        pontos.append(self._ponto_detalhe_do_pedido())
        pontos.append(self._ponto_relatorio())
        pontos.append(self._ponto_fila_de_moderacao())
        pontos.append(self._ponto_aprovar())
        pontos.append(self._ponto_cupom_criado())
        pontos.append(self._ponto_cupom_desativado())
        pontos.append(self._ponto_ebook_novo_entregue())
        return pontos

    # ── acesso ───────────────────────────────────────────────────────────

    def _ponto_recusa(self, nome: str, perfil: str, esperado: int, acao: str):
        """RBAC: comprador 403, visitante 401."""
        ponto = self._novo_ponto(nome, HISTORIA_ACESSO)
        resposta = self._chamar(ponto, perfil, "GET", "/api/v1/admin/products", acao)
        if resposta.status == esperado:
            ponto.concluir("VALIDO", "`" + perfil + "` recebe " + str(esperado) + " na API de administração.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "`" + perfil + "` recebeu " + str(resposta.status) + " (esperado " + str(esperado) + ")")
        return ponto

    def _ponto_login_do_painel(self):
        """O formulário do SQLAdmin, enviado como o navegador envia, abre o painel.

        A página do painel copia o `csrftoken` do cookie para o campo `csrf_token`
        do formulário; sem ele o CSRF recusa (contraste que prova a proteção ativa).
        """
        ponto = self._novo_ponto("Ponto 3 - Formulário de login do painel abre o painel", HISTORIA_ACESSO)
        http = self._nova_sessao()
        formulario = self._chamar_http(ponto, http, "", "GET", "/admin/login", "painel-formulario-de-login",
                                       procurar=["username", "password", "csrf_token"])
        conta = self._conta("admin")
        senha = self._segredo(self._adaptador.senha("admin"))
        sem_token = self._chamar_http(ponto, http, conta, "POST", "/admin/login", "painel-login-sem-csrf",
                                      formulario={"username": conta, "password": senha})
        token = self._segredo(str(http.cookies.get("csrftoken") or ""))
        envio = self._chamar_http(
            ponto, http, conta, "POST", "/admin/login", "painel-enviar-login",
            formulario={"username": conta, "password": senha, "csrf_token": token},
        )
        destino = self._cabecalho(envio, "location")
        if (formulario.status == 200 and sem_token.status == 403 and envio.status in (302, 303)
                and destino.rstrip("/").endswith("/admin")):
            ponto.concluir("VALIDO", "Sem token o login é recusado (403); com o token que a página põe no "
                           "formulário ele redireciona para o painel `/admin/`.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "sem token " + str(sem_token.status) + "; com token "
                           + str(envio.status) + " \"" + (self._detalhe(envio) or envio.texto[:80])
                           + "\" (destino `" + destino + "`)")
        return ponto

    # ── catálogo ─────────────────────────────────────────────────────────

    def _ponto_cadastro(self):
        """Cadastro nasce rascunho, fora da vitrine."""
        ponto = self._novo_ponto("Ponto 4 - E-book novo nasce como rascunho fora da vitrine", HISTORIA_CADASTRO)
        criado = self._chamar(ponto, "admin", "POST", "/api/v1/admin/products", "cadastrar-ebook",
                              corpo_json={"title": self.titulo, "price": "19.90", "author": "Equipe QA",
                                          "description": "E-book criado pelo QA."})
        corpo = criado.corpo if isinstance(criado.corpo, dict) else {}
        self.slug = str(corpo.get("slug", ""))
        if criado.status != 201 or not self.slug:
            ponto.concluir("FALHA DE PRODUTO", "cadastro respondeu " + str(criado.status) + " " + str(corpo)[:160])
            return ponto
        vitrine = self._chamar(ponto, "visitante", "GET", "/api/v1/products/" + self.slug, "rascunho-na-vitrine")
        if vitrine.status == 404:
            ponto.concluir("VALIDO", "O e-book `" + self.slug + "` é criado (201) e não abre na vitrine enquanto rascunho.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "o rascunho abre na vitrine (" + str(vitrine.status) + ")")
        return ponto

    def _ponto_arquivo_exe(self):
        """Upload de .exe é recusado."""
        ponto = self._novo_ponto("Ponto 5 - Arquivo exe é recusado como e-book", HISTORIA_CADASTRO)
        if not self.slug:
            ponto.concluir("EVIDENCIA INVALIDA", "sem o e-book do Ponto 4 não há onde subir o arquivo")
            return ponto
        resposta = self._chamar_http(
            ponto, self._adaptador.sessao("admin").http, self._conta("admin"), "POST",
            "/api/v1/admin/products/" + self.slug + "/upload-file", "upload-exe",
            arquivos={"file": ("virus.exe", b"MZ arquivo de teste do QA", "application/octet-stream")},
        )
        if 400 <= resposta.status < 500 and "formato" in self._detalhe(resposta).lower():
            ponto.concluir("VALIDO", "O `.exe` é recusado: " + str(resposta.status) + " \"" + self._detalhe(resposta) + "\".")
        else:
            ponto.concluir("FALHA DE PRODUTO", "upload de .exe respondeu " + str(resposta.status) + " " + self._detalhe(resposta))
        return ponto

    def _ponto_publicar(self):
        """Publicar coloca na vitrine."""
        ponto = self._novo_ponto("Ponto 6 - Publicar põe o e-book na vitrine", HISTORIA_CADASTRO)
        if not self.slug:
            ponto.concluir("EVIDENCIA INVALIDA", "sem o e-book do Ponto 4 não há o que publicar")
            return ponto
        publicado = self._chamar(ponto, "admin", "PATCH", "/api/v1/admin/products/" + self.slug + "/status",
                                 "publicar-ebook", corpo_json={"status": "published"})
        catalogo = self._chamar(ponto, "visitante", "GET", "/api/v1/products?page_size=50", "catalogo-depois-de-publicar")
        if publicado.status == 200 and self.slug in self._slugs(catalogo.corpo):
            ponto.concluir("VALIDO", "Depois de publicado, `" + self.slug + "` aparece no catálogo público.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "publicar " + str(publicado.status) + "; catálogo sem `" + self.slug + "`")
        return ponto

    # ── vendas ───────────────────────────────────────────────────────────

    def _ponto_lista_de_pedidos(self):
        """US-07: status, valor e data em cada pedido."""
        ponto = self._novo_ponto("Ponto 7 - Lista de pedidos traz status, valor e data", HISTORIA_VENDAS)
        resposta = self._chamar(ponto, "admin", "GET", "/api/v1/orders?page_size=50", "lista-de-pedidos")
        pedidos = resposta.corpo if isinstance(resposta.corpo, list) else []
        if resposta.status != 200 or not pedidos:
            ponto.concluir("FALHA DE PRODUTO", "lista de pedidos respondeu " + str(resposta.status) + " com " + str(len(pedidos)) + " pedido(s)")
            return ponto
        faltando = []
        for campo in ("status", "amount", "created_at"):
            if campo not in pedidos[0]:
                faltando.append(campo)
        if faltando:
            ponto.concluir("FALHA DE PRODUTO", "os pedidos da lista vêm sem " + ", ".join(faltando)
                           + " (campos: " + ", ".join(sorted(pedidos[0].keys())) + ")")
        else:
            ponto.concluir("VALIDO", "Cada pedido da lista traz status, valor e data.")
        return ponto

    def _ponto_detalhe_do_pedido(self):
        """RF-41: detalhe com itens."""
        ponto = self._novo_ponto("Ponto 8 - Detalhe do pedido traz itens e status", HISTORIA_VENDAS)
        referencia = self._adaptador.token_da_massa("referencia_do_pedido_pago")
        resposta = self._chamar(ponto, "admin", "GET", "/api/v1/orders/admin/" + referencia, "detalhe-do-pedido")
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        itens = corpo.get("items") or []
        if corpo.get("status") == "paid" and corpo.get("amount") == "99.80" and len(itens) == 2:
            ponto.concluir("VALIDO", "O detalhe traz o pedido pago de 99.80 com os 2 itens.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "detalhe: " + str(resposta.status) + " " + str(corpo)[:160])
        return ponto

    def _ponto_relatorio(self):
        """RF-42: relatório do período soma os pagos."""
        ponto = self._novo_ponto("Ponto 9 - Relatório de vendas do período soma os pedidos pagos", HISTORIA_VENDAS)
        hoje = datetime.now(timezone.utc).date()
        inicio = str(hoje - timedelta(days=1))
        fim = str(hoje + timedelta(days=1))
        resposta = self._chamar(ponto, "admin", "GET", "/api/v1/admin/reports/sales?date_from=" + inicio + "&date_to=" + fim,
                                "relatorio-de-vendas")
        corpo = resposta.corpo if isinstance(resposta.corpo, dict) else {}
        if int(corpo.get("orders_paid", 0) or 0) >= 1 and float(corpo.get("revenue_brl", 0) or 0) >= 99.80:
            ponto.concluir("VALIDO", "O relatório do período conta " + str(corpo.get("orders_paid")) + " pedido(s) pago(s), receita "
                           + str(corpo.get("revenue_brl")) + ".")
        else:
            ponto.concluir("FALHA DE PRODUTO", "relatório: " + str(resposta.status) + " " + str(corpo)[:160])
        return ponto

    # ── moderação ────────────────────────────────────────────────────────

    def _id_da_pendente(self, corpo) -> int:
        """Id da avaliação pendente da massa na fila (0 quando não está)."""
        if not isinstance(corpo, list):
            return 0
        for avaliacao in corpo:
            if COMENTARIO_PENDENTE in str(avaliacao.get("comment", "")):
                return int(avaliacao.get("id", 0))
        return 0

    def _ponto_fila_de_moderacao(self):
        """A pendente está na fila."""
        ponto = self._novo_ponto("Ponto 10 - Avaliação pendente está na fila de moderação", HISTORIA_MODERACAO)
        resposta = self._chamar(ponto, "admin", "GET", "/api/v1/admin/reviews?status=pending", "fila-de-moderacao")
        if self._id_da_pendente(resposta.corpo):
            ponto.concluir("VALIDO", "A fila de moderação contém a avaliação `qa-avaliacao-pendente`.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "a avaliação pendente não está na fila (" + str(resposta.status) + ")")
        return ponto

    def _ponto_aprovar(self):
        """Aprovar publica; contraste antes/depois."""
        ponto = self._novo_ponto("Ponto 11 - Aprovar publica a avaliação na página do e-book", HISTORIA_MODERACAO)
        fila = self._chamar(ponto, "admin", "GET", "/api/v1/admin/reviews?status=pending", "fila-antes-de-aprovar")
        identificador = self._id_da_pendente(fila.corpo)
        antes = self._chamar(ponto, "visitante", "GET", "/api/v1/products/arquitetura-limpa-web/reviews",
                             "avaliacoes-publicas-antes", procurar=[COMENTARIO_PENDENTE])
        if not identificador:
            ponto.concluir("EVIDENCIA INVALIDA", "sem avaliação pendente na fila não há o que aprovar")
            return ponto
        aprovacao = self._chamar(ponto, "admin", "PATCH", "/api/v1/admin/reviews/" + str(identificador) + "/moderate",
                                 "aprovar-avaliacao", corpo_json={"status": "approved"})
        depois = self._chamar(ponto, "visitante", "GET", "/api/v1/products/arquitetura-limpa-web/reviews",
                              "avaliacoes-publicas-depois", procurar=[COMENTARIO_PENDENTE])
        if COMENTARIO_PENDENTE not in antes.texto and aprovacao.status < 300 and COMENTARIO_PENDENTE in depois.texto:
            ponto.concluir("VALIDO", "O comentário não aparece antes e aparece na lista pública depois da aprovação.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "aprovação " + str(aprovacao.status) + "; visível antes="
                           + str(COMENTARIO_PENDENTE in antes.texto) + ", depois=" + str(COMENTARIO_PENDENTE in depois.texto))
        return ponto

    # ── cupons ───────────────────────────────────────────────────────────

    def _validar(self, ponto, acao: str):
        """Validação pública do cupom desta execução sobre 39.90."""
        return self._chamar(ponto, "visitante", "POST", "/api/v1/coupons/validate", acao,
                            corpo_json={"code": self.cupom, "amount": "39.90"})

    def _ponto_cupom_criado(self):
        """Criar e ver valer."""
        ponto = self._novo_ponto("Ponto 12 - Cupom criado passa a valer", HISTORIA_CUPONS)
        criado = self._chamar(ponto, "admin", "POST", "/api/v1/admin/coupons", "criar-cupom",
                              corpo_json={"code": self.cupom, "discount_type": "percent", "value": 20})
        validado = self._validar(ponto, "validar-cupom-criado")
        corpo = validado.corpo if isinstance(validado.corpo, dict) else {}
        if criado.status < 300 and corpo.get("valid") is True and corpo.get("total") == "31.92":
            ponto.concluir("VALIDO", "O cupom `" + self.cupom + "` é criado e vale: 39.90 → 31.92.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "criar " + str(criado.status) + "; validar " + str(validado.status) + " " + str(corpo)[:120])
        return ponto

    def _ponto_cupom_desativado(self):
        """Desativar e ver recusar."""
        ponto = self._novo_ponto("Ponto 13 - Cupom desativado deixa de valer", HISTORIA_CUPONS)
        alternado = self._chamar(ponto, "admin", "PATCH", "/api/v1/admin/coupons/" + self.cupom + "/toggle", "desativar-cupom")
        validado = self._validar(ponto, "validar-cupom-desativado")
        if alternado.status < 300 and 400 <= validado.status < 500:
            ponto.concluir("VALIDO", "Desativado, o cupom é recusado na validação (" + str(validado.status) + ").")
        else:
            ponto.concluir("FALHA DE PRODUTO", "desativar " + str(alternado.status) + "; validar " + str(validado.status))
        return ponto

    # ── ponta a ponta: cadastrar e vender ────────────────────────────────

    def _ponto_ebook_novo_entregue(self):
        """E-book criado pelo admin, com arquivo, chega a quem compra."""
        ponto = self._novo_ponto("Ponto 14 - E-book cadastrado com arquivo é entregue a quem compra", HISTORIA_CADASTRO)
        if not self.slug:
            ponto.concluir("EVIDENCIA INVALIDA", "sem o e-book do Ponto 4 não há o que vender")
            return ponto
        envio = self._chamar_http(
            ponto, self._adaptador.sessao("admin").http, self._conta("admin"), "POST",
            "/api/v1/admin/products/" + self.slug + "/upload-file", "upload-txt",
            arquivos={"file": ("ebook-qa.txt", CONTEUDO_SENTINELA.encode("utf-8"), "text/plain")},
        )
        pedido = self._chamar(ponto, "visitante", "POST", "/api/v1/orders", "pedido-do-ebook-novo",
                              corpo_json={"product_slug": self.slug,
                                          "buyer_email": "qa-convidado-novo-" + self._marca + "@eseller-qa.test"})
        referencia = str(pedido.corpo.get("reference", "")) if isinstance(pedido.corpo, dict) else ""
        if envio.status >= 300 or not referencia:
            ponto.concluir("FALHA DE PRODUTO", "upload " + str(envio.status) + "; pedido " + str(pedido.status))
            return ponto
        self._chamar(ponto, "visitante", "POST", "/api/v1/webhooks/mercadopago", "webhook-do-ebook-novo",
                     corpo_json={"provider_payment_id": "qa-webhook-" + referencia,
                                 "order_reference": referencia, "provider_status": "approved"})
        pagina = self._chamar(ponto, "visitante", "GET", "/pedido/" + referencia, "pedido-do-ebook-novo-pago",
                              procurar=["/api/v1/download/"])
        achado = PADRAO_LINK_DE_DOWNLOAD.search(pagina.texto)
        if not achado:
            ponto.concluir("FALHA DE PRODUTO", "o pedido pago não mostra link de download")
            return ponto
        token = self._segredo(achado.group(1))
        baixado = self._chamar_http(ponto, self._nova_sessao(), "", "GET", "/api/v1/download/" + token,
                                    "download-do-ebook-novo", procurar=[CONTEUDO_SENTINELA])
        disposicao = self._cabecalho(baixado, "content-disposition")
        if baixado.status == 200 and "attachment" in disposicao and CONTEUDO_SENTINELA in baixado.texto:
            ponto.concluir("VALIDO", "O e-book novo, com o .txt enviado pelo admin, é entregue como anexo a quem compra.")
        else:
            ponto.concluir("FALHA DE PRODUTO", "download do e-book novo: status " + str(baixado.status)
                           + " \"" + self._detalhe(baixado) + "\" — cadastrar e vender um e-book novo não entrega o arquivo")
        return ponto
