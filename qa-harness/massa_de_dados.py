"""Massa de dados do QA do e_seller — estado conhecido, gravado direto no Postgres de QA.

Regras (metodologia da skill /qa, seção 5):
- escreve direto na persistência, sem passar pelo código testado;
- tudo o que cria tem prefixo `qa-` (e-mail `qa-...@eseller-qa.test`, slug `qa-...`,
  cupom `QA-...`) e é apagado antes de ser recriado: rodar duas vezes dá o mesmo banco;
- cada regra tem contraste: `cliente` possui dois e-books pagos e `sem_compras` nada;
  um link de download válido, um esgotado e um expirado; uma avaliação pendente;
  `sem_compras` tem só um pedido pendente (pendente não dá posse).

A conta de admin é semeada pelo próprio backend no boot (APP_ENV=dev); aqui só se
confere que ela existe. Os tokens de download criados aqui voltam para o adaptador
em memória (nunca impressos) e as suítes os mascaram na evidência.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import psycopg


class GeradorDeHash:
    """Gera o hash de senha no formato do produto: `pbkdf2$iter$salt_hex$hash_hex`."""

    ITERACOES = 200_000

    def gerar(self, senha: str) -> str:
        """Hash PBKDF2-HMAC-SHA256 com salt aleatório de 16 bytes."""
        salt = secrets.token_bytes(16)
        derivado = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, self.ITERACOES)
        return "pbkdf2$" + str(self.ITERACOES) + "$" + salt.hex() + "$" + derivado.hex()


class MassaDeDados:
    """Recoloca o banco de QA no estado conhecido antes de cada execução."""

    PADRAO_EMAIL_QA = "qa-%@eseller-qa.test"
    PADRAO_CONTA_CRIADA_EM_JORNADA = "qa-novo-%@eseller-qa.test"
    PADRAO_SLUG_QA = "qa-%"
    PADRAO_CUPOM_QA = "QA-%"
    LIVROS_DO_CLIENTE = ["python-na-pratica", "arquitetura-limpa-web"]
    LIVRO_DA_AVALIACAO_PENDENTE = "arquitetura-limpa-web"
    COMENTARIO_DA_AVALIACAO_PENDENTE = "qa-avaliacao-pendente: texto conferido na moderação"

    def __init__(self, config, credenciais) -> None:
        """Recebe o config do harness e as credenciais locais da stack de QA."""
        self.config = config
        self.credenciais = credenciais
        self.gerador_de_hash = GeradorDeHash()
        self.tokens: dict = {}

    # ── conexão ──────────────────────────────────────────────────────────

    def conectar(self):
        """Conexão com o Postgres da stack de QA (porta do config.yaml)."""
        ambiente = self.config.dados.get("ambiente") or {}
        return psycopg.connect(
            host="127.0.0.1",
            port=int(ambiente.get("banco_porta", 0)),
            user=self.credenciais.valor("QA_POSTGRES_USER"),
            password=self.credenciais.valor("QA_POSTGRES_PASSWORD"),
            dbname=self.credenciais.valor("QA_POSTGRES_DB"),
            connect_timeout=5,
        )

    # ── verificações ─────────────────────────────────────────────────────

    def impedimentos(self) -> list:
        """O que impede a massa: banco fora, schema ausente, admin não semeado."""
        encontrados = []
        try:
            with self.conectar() as conexao:
                with conexao.cursor() as cursor:
                    cursor.execute("select count(*) from product where status = 'PUBLISHED'")
                    publicados = cursor.fetchone()[0]
                    if publicados < 3:
                        encontrados.append("catálogo de seed incompleto: " + str(publicados) + " publicado(s)")
                    cursor.execute(
                        "select role from \"user\" where email = %s", (self._conta("admin"),)
                    )
                    linha = cursor.fetchone()
                    if linha is None or linha[0] != "ADMIN":
                        encontrados.append("conta de admin do QA não foi semeada pelo backend")
        except Exception as erro:
            encontrados.append("banco de QA inacessível: " + type(erro).__name__ + ": " + str(erro)[:120])
        return encontrados

    # ── preparação ───────────────────────────────────────────────────────

    def preparar(self) -> dict:
        """Apaga o que é `qa-` e recria contas, pedidos pagos, links e avaliação."""
        self.tokens = {}
        with self.conectar() as conexao:
            with conexao.cursor() as cursor:
                self._apagar_tudo_que_e_qa(cursor)
                id_cliente = self._garantir_comprador(cursor, "cliente", "QA Cliente", "QA_CLIENTE_PASSWORD")
                id_sem_compras = self._garantir_comprador(cursor, "sem_compras", "QA Sem Compras", "QA_SEM_COMPRAS_PASSWORD")
                itens = self._criar_pedido_pago(cursor, id_cliente, self._conta("cliente"))
                self._criar_pedido_pendente(cursor, id_sem_compras, self._conta("sem_compras"))
                self._criar_links_de_download(cursor, itens)
                self._criar_avaliacao_pendente(cursor, id_cliente)
            conexao.commit()
        return self.tokens

    def _conta(self, perfil: str) -> str:
        """E-mail da conta do perfil no config.yaml."""
        return str(self.config.perfil(perfil).get("conta") or "")

    def _apagar_tudo_que_e_qa(self, cursor) -> None:
        """Remove, na ordem das chaves estrangeiras, tudo o que tem marca de QA."""
        cursor.execute(
            "select id from \"order\" where buyer_email like %s "
            "or user_id in (select id from \"user\" where email like %s)",
            (self.PADRAO_EMAIL_QA, self.PADRAO_EMAIL_QA),
        )
        pedidos = self._ids(cursor.fetchall())
        cursor.execute("select id from product where slug like %s", (self.PADRAO_SLUG_QA,))
        produtos = self._ids(cursor.fetchall())
        self._apagar_pedidos(cursor, pedidos, produtos)
        self._apagar_produtos(cursor, produtos)
        cursor.execute(
            "delete from coupon_redemption where coupon_id in (select id from coupon where code like %s)",
            (self.PADRAO_CUPOM_QA,),
        )
        cursor.execute("delete from coupon where code like %s", (self.PADRAO_CUPOM_QA,))
        cursor.execute("delete from newsletter_subscriber where email like %s", (self.PADRAO_EMAIL_QA,))
        cursor.execute("delete from login_attempt where email like %s", (self.PADRAO_EMAIL_QA,))
        self._apagar_dados_das_contas(cursor)
        self._apagar_contas_criadas_em_jornada(cursor)

    def _apagar_pedidos(self, cursor, pedidos: list, produtos: list) -> None:
        """Pedidos de QA (e os que citam produto de QA) com tudo o que depende deles."""
        if produtos:
            cursor.execute("select order_id from order_item where product_id = any(%s)", (produtos,))
            for linha in cursor.fetchall():
                if linha[0] not in pedidos:
                    pedidos.append(linha[0])
        if not pedidos:
            return
        cursor.execute("select id from order_item where order_id = any(%s)", (pedidos,))
        itens = self._ids(cursor.fetchall())
        if itens:
            cursor.execute(
                "delete from download_log where download_grant_id in "
                "(select id from download_grant where order_item_id = any(%s))",
                (itens,),
            )
            cursor.execute("delete from download_grant where order_item_id = any(%s)", (itens,))
            cursor.execute("delete from entitlement where order_item_id = any(%s)", (itens,))
        cursor.execute("delete from refund where order_id = any(%s)", (pedidos,))
        cursor.execute("delete from payment where order_id = any(%s)", (pedidos,))
        cursor.execute("delete from coupon_redemption where order_id = any(%s)", (pedidos,))
        cursor.execute("delete from order_item where order_id = any(%s)", (pedidos,))
        cursor.execute("delete from \"order\" where id = any(%s)", (pedidos,))

    def _apagar_produtos(self, cursor, produtos: list) -> None:
        """Produtos criados por jornadas/suítes de admin (slug `qa-...`)."""
        if not produtos:
            return
        for tabela in ("product_author", "product_tag", "product_file", "product_image",
                       "cart_item", "wishlist_item", "review", "entitlement"):
            cursor.execute("delete from " + tabela + " where product_id = any(%s)", (produtos,))
        cursor.execute("delete from download_grant where product_id = any(%s)", (produtos,))
        cursor.execute("delete from product where id = any(%s)", (produtos,))

    def _apagar_dados_das_contas(self, cursor) -> None:
        """Carrinho, favoritos, avaliações, posses e perfil fiscal das contas de QA."""
        contas = "(select id from \"user\" where email like %s)"
        parametros = (self.PADRAO_EMAIL_QA,)
        cursor.execute("delete from cart_item where cart_id in (select id from cart where user_id in " + contas + ")", parametros)
        cursor.execute("delete from wishlist_item where wishlist_id in (select id from wishlist where user_id in " + contas + ")", parametros)
        cursor.execute("delete from review where user_id in " + contas, parametros)
        cursor.execute("delete from entitlement where user_id in " + contas, parametros)
        cursor.execute("delete from billing_profile where user_id in " + contas
                       + " and id not in (select billing_profile_id from \"order\" where billing_profile_id is not null)",
                       parametros)

    def _apagar_contas_criadas_em_jornada(self, cursor) -> None:
        """Contas `qa-novo-...` criadas pela jornada de cadastro, com o que dependia delas."""
        contas = "(select id from \"user\" where email like %s)"
        parametros = (self.PADRAO_CONTA_CRIADA_EM_JORNADA,)
        for tabela in ("cart", "wishlist", "billing_profile", "api_key", "user_activity_log", "login_attempt"):
            cursor.execute("delete from " + tabela + " where user_id in " + contas, parametros)
        cursor.execute("delete from \"user\" where email like %s", parametros)

    def _garantir_comprador(self, cursor, perfil: str, nome: str, chave_da_senha: str) -> int:
        """Cria ou atualiza a conta de comprador do perfil com a senha local."""
        email = self._conta(perfil)
        hash_da_senha = self.gerador_de_hash.gerar(self.credenciais.valor(chave_da_senha))
        cursor.execute("select id from \"user\" where email = %s", (email,))
        linha = cursor.fetchone()
        if linha is None:
            cursor.execute(
                "insert into \"user\" (email, password_hash, full_name, role, is_active, totp_enabled) "
                "values (%s, %s, %s, 'CUSTOMER', true, false) returning id",
                (email, hash_da_senha, nome),
            )
            return cursor.fetchone()[0]
        cursor.execute(
            "update \"user\" set password_hash = %s, full_name = %s, role = 'CUSTOMER', "
            "is_active = true, deleted_at = null, totp_enabled = false, totp_secret_enc = null where id = %s",
            (hash_da_senha, nome, linha[0]),
        )
        return linha[0]

    def _criar_pedido_pago(self, cursor, id_usuario: int, email: str) -> list:
        """Pedido pago do cliente com os dois livros da massa; devolve os itens."""
        referencia = str(uuid.uuid4())
        total = 0
        produtos = []
        for slug in self.LIVROS_DO_CLIENTE:
            cursor.execute("select id, price from product where slug = %s", (slug,))
            produto = cursor.fetchone()
            produtos.append({"slug": slug, "id": produto[0], "preco": produto[1]})
            total = total + produto[1]
        cursor.execute(
            "insert into \"order\" (reference, buyer_email, user_id, amount, status) "
            "values (%s, %s, %s, %s, 'PAID') returning id",
            (referencia, email, id_usuario, total),
        )
        id_pedido = cursor.fetchone()[0]
        cursor.execute(
            "insert into payment (order_id, provider, provider_payment_id, status, processed_at) "
            "values (%s, 'fake', %s, 'approved', now())",
            (id_pedido, "qa-massa-" + referencia),
        )
        itens = []
        for produto in produtos:
            cursor.execute(
                "insert into order_item (order_id, product_id, unit_price, quantity) "
                "values (%s, %s, %s, 1) returning id",
                (id_pedido, produto["id"], produto["preco"]),
            )
            id_item = cursor.fetchone()[0]
            cursor.execute(
                "insert into entitlement (user_id, product_id, order_item_id) values (%s, %s, %s)",
                (id_usuario, produto["id"], id_item),
            )
            itens.append({"slug": produto["slug"], "id_item": id_item, "id_produto": produto["id"]})
        self.tokens["referencia_do_pedido_pago"] = referencia
        return itens

    def _criar_pedido_pendente(self, cursor, id_usuario: int, email: str) -> None:
        """Pedido pendente de `arquitetura-limpa-web` (59.90), sem pagamento nem posse."""
        cursor.execute("select id, price from product where slug = 'arquitetura-limpa-web'")
        produto = cursor.fetchone()
        referencia = str(uuid.uuid4())
        cursor.execute(
            "insert into \"order\" (reference, buyer_email, user_id, amount, status) "
            "values (%s, %s, %s, %s, 'PENDING') returning id",
            (referencia, email, id_usuario, produto[1]),
        )
        id_pedido = cursor.fetchone()[0]
        cursor.execute(
            "insert into order_item (order_id, product_id, unit_price, quantity) values (%s, %s, %s, 1)",
            (id_pedido, produto[0], produto[1]),
        )
        self.tokens["referencia_do_pedido_pendente"] = referencia

    def _criar_links_de_download(self, cursor, itens: list) -> None:
        """Três links do primeiro livro: válido, esgotado (5/5) e expirado."""
        primeiro = itens[0]
        agora = datetime.now(timezone.utc)
        variantes = [
            ("download_valido", agora + timedelta(days=7), 0),
            ("download_esgotado", agora + timedelta(days=7), 5),
            ("download_expirado", agora - timedelta(days=1), 0),
        ]
        for nome, expira_em, baixados in variantes:
            token = secrets.token_urlsafe(32)
            cursor.execute(
                "insert into download_grant (order_item_id, product_id, token, expires_at, max_downloads, download_count) "
                "values (%s, %s, %s, %s, 5, %s)",
                (primeiro["id_item"], primeiro["id_produto"], token, expira_em, baixados),
            )
            self.tokens[nome] = token

    def _criar_avaliacao_pendente(self, cursor, id_usuario: int) -> None:
        """Avaliação pendente do cliente, que a moderação do admin aprova."""
        cursor.execute("select id from product where slug = %s", (self.LIVRO_DA_AVALIACAO_PENDENTE,))
        id_produto = cursor.fetchone()[0]
        cursor.execute(
            "insert into review (product_id, user_id, rating, comment, status) "
            "values (%s, %s, 5, %s, 'PENDING')",
            (id_produto, id_usuario, self.COMENTARIO_DA_AVALIACAO_PENDENTE),
        )

    def _ids(self, linhas: list) -> list:
        """Primeira coluna de cada linha de um fetchall."""
        valores = []
        for linha in linhas:
            valores.append(linha[0])
        return valores

    # ── limpeza pedida por jornada ───────────────────────────────────────

    def limpar(self, limpeza: dict) -> None:
        """Limpeza declarada na jornada: `recurso` (ou lista `recursos`) de uma conta.

        carrinho · favoritos · avaliacao (do `slug`) · pedidos-pendentes ·
        compras (pedidos da conta que contêm o `slug`, com posse e links).
        """
        recursos = limpeza.get("recursos") or [limpeza.get("recurso", "")]
        conta = self._conta(str(limpeza.get("perfil", "cliente")))
        slug = str(limpeza.get("slug", ""))
        contas = "(select id from \"user\" where email = %s)"
        with self.conectar() as conexao:
            with conexao.cursor() as cursor:
                for recurso in recursos:
                    if recurso == "carrinho":
                        cursor.execute("delete from cart_item where cart_id in (select id from cart where user_id in " + contas + ")", (conta,))
                    elif recurso == "favoritos":
                        cursor.execute("delete from wishlist_item where wishlist_id in (select id from wishlist where user_id in " + contas + ")", (conta,))
                    elif recurso == "avaliacao":
                        cursor.execute(
                            "delete from review where user_id in " + contas + " and product_id = (select id from product where slug = %s)",
                            (conta, slug),
                        )
                    elif recurso == "pedidos-pendentes":
                        cursor.execute("select id from \"order\" where status = 'PENDING' and user_id in " + contas, (conta,))
                        self._apagar_pedidos(cursor, self._ids(cursor.fetchall()), [])
                    elif recurso == "compras":
                        cursor.execute(
                            "select distinct o.id from \"order\" o join order_item i on i.order_id = o.id "
                            "join product p on p.id = i.product_id where p.slug = %s and o.user_id in " + contas,
                            (slug, conta),
                        )
                        self._apagar_pedidos(cursor, self._ids(cursor.fetchall()), [])
            conexao.commit()
