"""Base visual — retrato do sistema tela a tela, por perfil, independente de história.

Captura exatamente o que está declarado no catálogo (`caminhos.base_visual`,
padrão `spec/test/planos/_base-visual.yaml`); não descobre telas sozinha. Tela
nova no produto é entrada nova no catálogo, e o diff prova.

Formato do catálogo:
    perfis:
      visitante:
        telas:
          - { nome: 01-home, rota: "/" }
      assinante:
        rota_home: "/app"                        # só para telas por aba
        telas:
          - { nome: 01-feed, rota: "/app/feed" }
          - { nome: 02-perfil, aba: "Perfil" }    # clica no botão/aba com esse texto
          - { nome: 03-aviso, rota: "/aviso", texto_minimo: 80 }   # tela curta por design

Evidência: `evidencias/_base/<perfil>/<viewport>/<nome>.png` + `evidencias.json`.
Um ponto por perfil e viewport.
"""

from playwright.sync_api import sync_playwright

from .evidencia import ResultadoDoPonto
from .evidencia_de_pasta import EvidenciaDePasta, limpar_pasta_de_imagens
from .navegador import Navegador


class BaseVisual:
    """Percorre o catálogo e devolve um ponto por perfil e viewport."""

    def __init__(self, config, adaptador, especificacao, viewports: list) -> None:
        self._config = config
        self._adaptador = adaptador
        self._catalogo = especificacao.catalogo_da_base_visual()
        self._viewports = viewports
        self._navegador = Navegador(config, adaptador)

    def executar(self) -> list:
        """Captura todos os perfis em todos os viewports pedidos."""
        pontos = []
        perfis = self._catalogo.get("perfis") or {}
        if not perfis:
            print("    catálogo da base visual vazio ou ausente — nada a capturar")
            return pontos
        with sync_playwright() as playwright:
            for nome_do_viewport in self._viewports:
                for nome_do_perfil in perfis:
                    navegador = self._navegador.lancar(playwright)
                    ponto = self._capturar_perfil(
                        navegador, nome_do_perfil, perfis[nome_do_perfil] or {}, nome_do_viewport
                    )
                    navegador.close()
                    pontos.append(ponto)
                    print("    - " + ponto.nome + ": " + ponto.veredito)
        return pontos

    def _capturar_perfil(self, navegador, perfil: str, dados: dict, viewport: str):
        pasta = self._config.caminho("evidencias") / "_base" / perfil / viewport
        limpar_pasta_de_imagens(pasta)
        pacote = EvidenciaDePasta(
            pasta,
            self._config.raiz_projeto,
            gerado_por="motor/base_visual.py",
            extra={"perfil": perfil, "viewport": viewport},
        )
        ponto = ResultadoDoPonto(
            "Base visual - " + perfil + " (" + viewport + ")",
            "Base visual - " + perfil,
            "base",
            "base-visual",
            viewport,
        )
        contexto = self._navegador.novo_contexto(navegador, viewport)
        erros_de_console: list = []
        pagina = self._navegador.nova_pagina(contexto, erros_de_console)
        problemas: list = []

        try:
            entrou = self._navegador.entrar(contexto, pagina, perfil)
        except Exception as erro:
            entrou = False
            problemas.append("falha ao entrar: " + str(erro)[:160])
        if not entrou:
            ponto.concluir(
                "EVIDENCIA INVALIDA",
                "não foi possível entrar como " + perfil + " — telas do perfil não capturadas. "
                + "; ".join(problemas),
            )
            contexto.close()
            return ponto

        telas = dados.get("telas") or []
        ordem = 0
        for tela in telas:
            ordem = ordem + 1
            self._capturar_tela(pagina, pasta, pacote, ponto, tela, dados, ordem, problemas)

        pacote.anotar("problemas", problemas)
        pacote.anotar("erros_de_console", erros_de_console)
        pacote.gravar()
        contexto.close()

        ponto.anotar_extra("erros_de_console", erros_de_console)
        ponto.anotar_extra("problemas", problemas)
        resumo = str(len(telas)) + " tela(s) em " + viewport
        if erros_de_console:
            resumo = resumo + "; " + str(len(erros_de_console)) + " erro(s) de console"
        if problemas:
            ponto.concluir("FALHA DE PRODUTO", resumo + ". Problemas: " + "; ".join(problemas))
        else:
            ponto.concluir(
                "VALIDO",
                resumo + ". Todas renderizaram conteúdo, sem rolagem horizontal.",
            )
        return ponto

    def _capturar_tela(self, pagina, pasta, pacote, ponto, tela, dados, ordem, problemas) -> None:
        nome = str(tela.get("nome") or str(ordem).zfill(2))
        arquivo = nome + ".png"
        pedido = tela.get("rota") or ("aba " + str(tela.get("aba")))
        falha = ""
        try:
            if tela.get("rota"):
                self._navegador.ir(pagina, str(tela["rota"]))
            elif tela.get("aba"):
                if dados.get("rota_home") and not pagina.url.endswith(str(dados["rota_home"])):
                    self._navegador.ir(pagina, str(dados["rota_home"]))
                pagina.get_by_text(str(tela["aba"]), exact=True).first.click()
                self._navegador.assentar(pagina)
            else:
                falha = "tela sem rota nem aba no catálogo"
        except Exception as erro:
            falha = str(erro).splitlines()[0][:200]
        self._navegador.fotografar(pagina, pasta / arquivo)
        medida = self._navegador.medir(pagina)
        medida["tela"] = nome
        medida["pedido"] = pedido
        medida["falha_ao_abrir"] = falha
        pacote.registrar(arquivo, medida)

        minimo = int(tela.get("texto_minimo", self._config.texto_minimo_renderizado))
        if falha:
            problemas.append(nome + " falhou ao abrir: " + falha)
        elif medida["texto_renderizado"] < minimo:
            problemas.append(
                nome + " renderizou só " + str(medida["texto_renderizado"]) + " caracteres"
            )
        if medida.get("scroll_horizontal"):
            problemas.append(
                nome + " tem rolagem horizontal ("
                + str(medida["scrollWidth"]) + "px > " + str(medida["innerWidth"]) + "px)"
            )
        ponto.anotar_passo(
            ordem,
            "tela",
            nome + " — " + str(pedido),
            self._config.relativo(pasta / arquivo),
            {"url": medida["url"], "texto_renderizado": medida["texto_renderizado"]},
        )
