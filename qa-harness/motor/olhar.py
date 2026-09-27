"""Print avulso de uma tela — ferramenta de revisão, não prova de história.

Serve para o QA olhar uma tela durante o ciclo revisão → healing → revalidação
sem rodar a base inteira nem uma jornada. A evidência que sustenta veredito
continua vindo da base visual e das jornadas; `_olhar/` não entra no manifesto.

Saída: `evidencias/_olhar/<perfil>-<rota>/<viewport>/tela.png` + `evidencias.json`.
"""

from playwright.sync_api import sync_playwright

from .evidencia import criar_apelido
from .evidencia_de_pasta import EvidenciaDePasta, limpar_pasta_de_imagens
from .navegador import Navegador


class OlharTela:
    """Abre uma rota com o perfil pedido e grava um print com a medida."""

    def __init__(self, config, adaptador) -> None:
        self._config = config
        self._navegador = Navegador(config, adaptador)

    def executar(self, rota: str, perfil: str, viewport: str) -> int:
        apelido = criar_apelido(perfil + "-" + rota, 80) or "raiz"
        pasta = self._config.caminho("evidencias") / "_olhar" / apelido / viewport
        limpar_pasta_de_imagens(pasta)
        pacote = EvidenciaDePasta(
            pasta, self._config.raiz_projeto, gerado_por="motor/olhar.py",
            extra={"rota": rota, "perfil": perfil, "viewport": viewport},
        )
        erros: list = []
        with sync_playwright() as playwright:
            navegador = self._navegador.lancar(playwright)
            contexto = self._navegador.novo_contexto(navegador, viewport)
            pagina = self._navegador.nova_pagina(contexto, erros)
            if not self._navegador.entrar(contexto, pagina, perfil):
                print("não consegui entrar como " + perfil)
                navegador.close()
                return 1
            falha = ""
            try:
                self._navegador.ir(pagina, rota)
            except Exception as erro:
                falha = str(erro).splitlines()[0][:200]
            self._navegador.fotografar(pagina, pasta / "tela.png")
            medida = self._navegador.medir(pagina)
            medida["falha_ao_abrir"] = falha
            medida["erros_de_console"] = erros
            pacote.registrar("tela.png", medida)
            pacote.gravar()
            navegador.close()
        print("print: " + self._config.relativo(pasta / "tela.png"))
        print("url final: " + str(medida["url"]) + " · texto: " + str(medida["texto_renderizado"])
              + " caracteres · rolagem horizontal: " + ("sim" if medida["scroll_horizontal"] else "não"))
        if erros:
            print(str(len(erros)) + " erro(s) de console: " + erros[0][:160])
        return 0
