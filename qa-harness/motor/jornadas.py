"""Jornadas de usuário — uma funcionalidade percorrida do início ao fim, um print por passo.

As jornadas são declaradas em `spec/test/jornadas/<dominio>.yaml` (contrato em
`_contrato.yaml` da mesma pasta). Cada passo vira uma captura com a sua entrada
no `evidencias.json` da pasta; o primeiro passo é marcado INICIO e o último FIM.

Vocabulário de passo (cada ação é um método `_acao_<nome>`):
  abrir {rota} · clicar {texto|seletor|aba} · preencher {campo|tipo|seletor, valor}
  selecionar {campo|seletor, opcao|indice} · teclar {tecla, campo|seletor?}
  esperar {ms} · entrar_como {perfil}
  conferir_texto {texto, dentro_de?} · conferir_ausencia {texto, dentro_de?}
  conferir_url {termina_em|contem} · conferir_elemento {seletor}

Veredito: passo de conferência que não se confirma → FALHA DE PRODUTO; passo que
não consegue ser executado (seletor ausente, ação desconhecida, navegação que
estoura) → EVIDENCIA INVALIDA, porque a jornada não chegou a provar nada.
"""

import time

from playwright.sync_api import sync_playwright

from .evidencia import ResultadoDoPonto, criar_apelido
from .evidencia_de_pasta import EvidenciaDePasta, limpar_pasta_de_imagens
from .navegador import Navegador

ACOES_DE_VERIFICACAO = (
    "conferir_texto",
    "conferir_ausencia",
    "conferir_url",
    "conferir_elemento",
)


class ErroDeExecucao(Exception):
    """O passo não pôde ser executado — a jornada não provou nada."""


class ErroDeConferencia(Exception):
    """O passo executou e o resultado esperado não apareceu."""


class ExecutorDePassos:
    """Traduz um passo declarado em ação do Playwright."""

    INTERVALO_DE_CONFERENCIA_MS = 500

    def __init__(self, config, navegador: Navegador, contexto, pagina) -> None:
        self._config = config
        self._navegador = navegador
        self._contexto = contexto
        self._pagina = pagina

    def executar(self, passo: dict) -> dict:
        """Executa o passo e devolve o que foi observado."""
        acao = str(passo.get("acao", ""))
        metodo = getattr(self, "_acao_" + acao, None)
        if metodo is None:
            raise ErroDeExecucao("ação desconhecida no YAML: " + acao)
        observado = metodo(passo)
        return observado or {}

    # ── navegação ────────────────────────────────────────────────────────

    def _acao_abrir(self, passo: dict) -> dict:
        rota = str(passo["rota"])
        try:
            self._navegador.ir(self._pagina, rota)
        except Exception as erro:
            raise ErroDeExecucao("não consegui abrir " + rota + ": " + self._resumo(erro))
        return {"rota_pedida": rota, "url_final": self._pagina.url}

    def _acao_esperar(self, passo: dict) -> dict:
        milissegundos = int(passo.get("ms", 1000))
        self._pagina.wait_for_timeout(milissegundos)
        return {"esperou_ms": milissegundos}

    def _acao_entrar_como(self, passo: dict) -> dict:
        perfil = str(passo["perfil"])
        try:
            entrou = self._navegador.entrar(self._contexto, self._pagina, perfil)
        except Exception as erro:
            raise ErroDeExecucao("não consegui entrar como " + perfil + ": " + self._resumo(erro))
        if not entrou:
            raise ErroDeExecucao("não consegui entrar como " + perfil)
        if passo.get("rota"):
            self._navegador.ir(self._pagina, str(passo["rota"]))
        return {"entrou_como": perfil, "url_final": self._pagina.url}

    # ── interação ────────────────────────────────────────────────────────

    def _acao_clicar(self, passo: dict) -> dict:
        alvo = self._alvo_de_clique(passo)
        try:
            alvo.first.click(timeout=self._config.timeout_ms)
        except Exception as erro:
            raise ErroDeExecucao("não consegui clicar: " + self._resumo(erro))
        self._navegador.assentar(self._pagina)
        return {"clicou_em": self._descrever(passo), "url_final": self._pagina.url}

    def _acao_preencher(self, passo: dict) -> dict:
        seletor = self._seletor_de_campo(passo)
        valor = str(passo["valor"])
        try:
            self._pagina.locator(seletor).first.fill(valor, timeout=self._config.timeout_ms)
        except Exception as erro:
            raise ErroDeExecucao("não consegui preencher " + seletor + ": " + self._resumo(erro))
        return {"campo": seletor, "valor": valor}

    def _acao_teclar(self, passo: dict) -> dict:
        """Pressiona uma tecla (Enter, Escape, Tab...) no campo indicado ou no foco atual.

        Formulário que só envia com Enter (busca sem botão) não tem outro caminho
        de prova: preencher não dispara tecla nenhuma.
        """
        tecla = str(passo.get("tecla", ""))
        if not tecla:
            raise ErroDeExecucao("teclar exige 'tecla' (ex.: Enter)")
        try:
            if "seletor" in passo or "campo" in passo:
                seletor = self._seletor_de_campo(passo)
                self._pagina.locator(seletor).first.press(tecla, timeout=self._config.timeout_ms)
            else:
                self._pagina.keyboard.press(tecla)
        except Exception as erro:
            raise ErroDeExecucao("não consegui teclar " + tecla + ": " + self._resumo(erro))
        self._navegador.assentar(self._pagina)
        return {"teclou": tecla, "url_final": self._pagina.url}

    def _acao_selecionar(self, passo: dict) -> dict:
        seletor = self._seletor_de_campo(passo)
        alvo = self._pagina.locator(seletor).first
        try:
            if "opcao" in passo:
                alvo.select_option(label=str(passo["opcao"]), timeout=self._config.timeout_ms)
                escolhido = str(passo["opcao"])
            else:
                indice = int(passo.get("indice", 1))
                opcoes = alvo.locator("option").all_inner_texts()
                if indice >= len(opcoes):
                    raise ErroDeExecucao(
                        seletor + " tem " + str(len(opcoes)) + " opção(ões); pedi a " + str(indice)
                    )
                alvo.select_option(index=indice, timeout=self._config.timeout_ms)
                escolhido = opcoes[indice]
        except ErroDeExecucao:
            raise
        except Exception as erro:
            raise ErroDeExecucao("não consegui selecionar em " + seletor + ": " + self._resumo(erro))
        return {"campo": seletor, "escolheu": escolhido}

    # ── verificação ──────────────────────────────────────────────────────

    def _acao_conferir_texto(self, passo: dict) -> dict:
        """O texto precisa aparecer renderizado — sem diferenciar caixa."""
        texto = str(passo["texto"])
        onde = str(passo.get("dentro_de", "body"))
        procurado = texto.casefold()
        limite = time.monotonic() + self._config.timeout_ms / 1000
        while True:
            conteudo = self._texto_de(onde)
            if procurado in conteudo.casefold():
                self._trazer_texto_a_vista(texto, onde)
                return {"conferiu_texto": texto, "dentro_de": onde}
            if time.monotonic() >= limite:
                raise ErroDeConferencia('não achei "' + texto + '" em ' + onde)
            self._pagina.wait_for_timeout(self.INTERVALO_DE_CONFERENCIA_MS)

    def _acao_conferir_ausencia(self, passo: dict) -> dict:
        texto = str(passo["texto"])
        onde = str(passo.get("dentro_de", "body"))
        conteudo = self._texto_de(onde)
        if texto.casefold() in conteudo.casefold():
            raise ErroDeConferencia('"' + texto + '" está na tela e não deveria')
        return {"conferiu_ausencia": texto, "dentro_de": onde}

    def _acao_conferir_url(self, passo: dict) -> dict:
        termina_em = str(passo.get("termina_em", "")).rstrip("/")
        contem = str(passo.get("contem", ""))
        if not termina_em and not contem:
            raise ErroDeExecucao("conferir_url exige 'termina_em' ou 'contem'")
        limite = time.monotonic() + self._config.timeout_ms / 1000
        while True:
            atual = self._pagina.url
            sem_consulta = atual.split("?")[0].rstrip("/")
            if termina_em and sem_consulta.endswith(termina_em):
                return {"url_final": atual}
            if contem and contem in atual:
                return {"url_final": atual}
            if time.monotonic() >= limite:
                esperado = termina_em or contem
                raise ErroDeConferencia("a URL é " + atual + ", esperava " + esperado)
            self._pagina.wait_for_timeout(self.INTERVALO_DE_CONFERENCIA_MS)

    def _acao_conferir_elemento(self, passo: dict) -> dict:
        seletor = str(passo["seletor"])
        try:
            self._pagina.locator(seletor).first.wait_for(
                state="visible", timeout=self._config.timeout_ms
            )
        except Exception:
            raise ErroDeConferencia("nenhum elemento visível para " + seletor)
        try:
            self._pagina.locator(seletor).first.scroll_into_view_if_needed(timeout=2000)
        except Exception:
            pass
        return {"conferiu_elemento": seletor}

    # ── apoio ────────────────────────────────────────────────────────────

    def _trazer_texto_a_vista(self, texto: str, onde: str) -> None:
        """Rola até o primeiro trecho visível com o texto: o print mostra a prova."""
        try:
            candidatos = self._pagina.locator(onde).first.get_by_text(texto, exact=False)
            quantidade = min(candidatos.count(), 10)
            indice = 0
            while indice < quantidade:
                candidato = candidatos.nth(indice)
                if candidato.is_visible():
                    candidato.scroll_into_view_if_needed(timeout=2000)
                    return
                indice = indice + 1
        except Exception:
            return

    def _texto_de(self, onde: str) -> str:
        try:
            return self._pagina.locator(onde).first.inner_text(timeout=2000)
        except Exception:
            return ""

    def _alvo_de_clique(self, passo: dict):
        if "seletor" in passo:
            return self._pagina.locator(str(passo["seletor"]))
        if "aba" in passo:
            return self._pagina.get_by_role("tab", name=str(passo["aba"])).or_(
                self._pagina.get_by_role("button", name=str(passo["aba"]))
            )
        if "texto" in passo:
            return self._pagina.get_by_text(str(passo["texto"]), exact=False)
        raise ErroDeExecucao("clicar exige 'texto', 'aba' ou 'seletor'")

    def _seletor_de_campo(self, passo: dict) -> str:
        if "seletor" in passo:
            return str(passo["seletor"])
        if "campo" in passo:
            return '[name="' + str(passo["campo"]) + '"]'
        if "tipo" in passo:
            return "input[type=" + str(passo["tipo"]) + "]"
        raise ErroDeExecucao("preencher/selecionar exige 'campo', 'tipo' ou 'seletor'")

    def _descrever(self, passo: dict) -> str:
        for chave in ("seletor", "aba", "texto"):
            if chave in passo:
                return chave + "=" + str(passo[chave])
        return "?"

    def _resumo(self, erro: Exception) -> str:
        linhas = str(erro).strip().splitlines()
        if not linhas:
            return type(erro).__name__
        return linhas[0][:200]


class Jornada:
    """Uma funcionalidade percorrida do início ao fim, com print a cada passo."""

    def __init__(self, dados: dict, config, adaptador, marca: str) -> None:
        self._dados = interpolar(dados, marca)
        self._config = config
        self._adaptador = adaptador
        self._dominio = str(dados.get("_dominio", ""))
        self._navegador = Navegador(config, adaptador)

    @property
    def identificador(self) -> str:
        return str(self._dados.get("id", ""))

    def executar(self, navegador_pw, nome_do_viewport: str) -> ResultadoDoPonto:
        pasta = (
            self._config.caminho("evidencias")
            / "jornadas"
            / self._dominio
            / self.identificador
            / nome_do_viewport
        )
        limpar_pasta_de_imagens(pasta)
        passos = self._dados.get("passos") or []
        pacote = EvidenciaDePasta(
            pasta,
            self._config.raiz_projeto,
            gerado_por="motor/jornadas.py",
            extra={
                "jornada": self.identificador,
                "nome": self._dados.get("nome", ""),
                "historia": self._dados.get("historia", ""),
                "dominio": self._dominio,
                "viewport": nome_do_viewport,
                "passos_declarados": len(passos),
            },
        )
        ponto = ResultadoDoPonto(
            "Jornada - " + str(self._dados.get("nome", self.identificador)),
            str(self._dados.get("historia", "")),
            "jornada",
            self._dominio,
            nome_do_viewport,
        )
        ponto.anotar_extra("jornada", self.identificador)
        ponto.anotar_extra("jornada_arquivo", self._dados.get("_arquivo", ""))
        ponto.anotar_extra("ator", self._dados.get("ator", ""))

        self._limpar_execucao_anterior()
        contexto = self._navegador.novo_contexto(navegador_pw, nome_do_viewport)
        erros_de_console: list = []
        pagina = self._navegador.nova_pagina(contexto, erros_de_console)
        executor = ExecutorDePassos(self._config, self._navegador, contexto, pagina)

        veredito = "VALIDO"
        problema = ""
        entrada = str(self._dados.get("entra_como") or "visitante")
        try:
            if not self._navegador.entrar(contexto, pagina, entrada):
                veredito = "EVIDENCIA INVALIDA"
                problema = "não consegui entrar como " + entrada
        except Exception as erro:
            veredito = "EVIDENCIA INVALIDA"
            problema = "não consegui entrar como " + entrada + ": " + str(erro)[:160]

        executados = 0
        if not problema:
            total = len(passos)
            for indice, passo in enumerate(passos):
                marco = marco_do_passo(indice, total)
                titulo = str(passo.get("titulo") or passo.get("acao"))
                try:
                    observado = executor.executar(passo)
                except ErroDeConferencia as erro:
                    veredito = "FALHA DE PRODUTO"
                    problema = "passo " + str(indice + 1) + " (" + titulo + "): " + str(erro)
                    observado = {"erro": str(erro)}
                except ErroDeExecucao as erro:
                    veredito = "EVIDENCIA INVALIDA"
                    problema = "passo " + str(indice + 1) + " (" + titulo + "): " + str(erro)
                    observado = {"erro": str(erro)}
                executados = indice + 1
                self._gravar_passo(pagina, pacote, ponto, pasta, indice + 1, passo, marco, titulo, observado)
                if problema:
                    break

        pacote.anotar("passos_executados", executados)
        pacote.anotar("veredito", veredito)
        pacote.anotar("problema", problema)
        pacote.anotar("erros_de_console", erros_de_console)
        pacote.gravar()
        contexto.close()

        ponto.anotar_extra("passos_declarados", len(passos))
        ponto.anotar_extra("passos_executados", executados)
        ponto.anotar_extra("erros_de_console", erros_de_console)
        resumo = str(executados) + "/" + str(len(passos)) + " passos"
        if erros_de_console:
            resumo = resumo + "; " + str(len(erros_de_console)) + " erro(s) de console"
        if problema:
            ponto.concluir(veredito, resumo + ". " + problema)
        else:
            ponto.concluir(
                "VALIDO",
                resumo + ", do início ao fim, com todas as conferências confirmadas na tela.",
            )
        return ponto

    def _gravar_passo(self, pagina, pacote, ponto, pasta, numero, passo, marco, titulo, observado) -> None:
        nome = str(numero).zfill(2) + "-" + criar_apelido(titulo, 60) + ".png"
        self._navegador.fotografar_janela(pagina, pasta / nome)
        medida = self._navegador.medir(pagina)
        registro = {
            "passo": numero,
            "marco": marco,
            "titulo": titulo,
            "acao": passo.get("acao"),
            "observado": observado,
        }
        registro.update(medida)
        pacote.registrar(nome, registro)
        ponto.anotar_passo(numero, marco, titulo, self._config.relativo(pasta / nome), observado)

    def _limpar_execucao_anterior(self) -> None:
        limpeza = self._dados.get("limpeza")
        if not limpeza:
            return
        try:
            self._adaptador.limpar(limpeza)
        except Exception as erro:
            print("      aviso: limpeza falhou (" + type(erro).__name__ + ": " + str(erro)[:120] + ")")


class RunnerDeJornadas:
    """Executa as jornadas declaradas, filtrando por domínio ou por id."""

    def __init__(self, config, adaptador, especificacao, viewport: str,
                 dominios: list = None, so_jornada: str = "") -> None:
        self._config = config
        self._adaptador = adaptador
        self._especificacao = especificacao
        self._viewport = viewport
        self._dominios = list(dominios or [])
        self._so_jornada = so_jornada
        self._marca = time.strftime("%d%H%M%S")

    def executar(self) -> list:
        selecionadas = self._selecionar()
        pontos = []
        if not selecionadas:
            print("    nenhuma jornada declarada em " + self._config.relativo(self._config.caminho("jornadas")))
            return pontos
        navegador_auxiliar = Navegador(self._config, self._adaptador)
        with sync_playwright() as playwright:
            for dados in selecionadas:
                jornada = Jornada(dados, self._config, self._adaptador, self._marca)
                navegador = navegador_auxiliar.lancar(playwright)
                inicio = time.monotonic()
                ponto = jornada.executar(navegador, self._viewport)
                navegador.close()
                ponto.anotar_extra("segundos", round(time.monotonic() - inicio, 1))
                pontos.append(ponto)
                print("    - [" + ponto.veredito + "] " + ponto.nome + " — " + ponto.detalhe[:140])
        return pontos

    def _selecionar(self) -> list:
        selecionadas = []
        for dados in self._especificacao.jornadas():
            if self._dominios and dados.get("_dominio") not in self._dominios:
                continue
            if self._so_jornada and dados.get("id") != self._so_jornada:
                continue
            selecionadas.append(dados)
        return selecionadas


def marco_do_passo(indice: int, total: int) -> str:
    """O PDF mostra onde a funcionalidade começa e onde termina."""
    if indice == 0:
        return "INICIO"
    if indice == total - 1:
        return "FIM"
    return "passo"


def interpolar(valor, marca: str):
    """Troca `{{execucao}}` pela marca desta execução, em qualquer profundidade.

    O que a jornada cria ganha identidade única, e a conferência não enxerga o
    registro deixado pela execução anterior.
    """
    if isinstance(valor, str):
        return valor.replace("{{execucao}}", marca)
    if isinstance(valor, list):
        convertida = []
        for item in valor:
            convertida.append(interpolar(item, marca))
        return convertida
    if isinstance(valor, dict):
        convertido = {}
        for chave in valor:
            convertido[chave] = interpolar(valor[chave], marca)
        return convertido
    return valor
