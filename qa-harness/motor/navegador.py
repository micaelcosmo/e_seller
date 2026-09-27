"""Navegador comum à base visual, às jornadas e ao `olhar`.

Medir uma tela cedo demais registra tela em branco ou a URL de antes de um
redirecionamento do lado do cliente — e isso vira falha de produto que não
existe. Por isso toda navegação passa por `assentar`, que só devolve a tela
quando a URL parou de mudar e o texto renderizado se firmou.
"""

from pathlib import Path


class Navegador:
    """Abre contextos por viewport e padroniza navegação, medida e captura."""

    def __init__(self, config, adaptador) -> None:
        self._config = config
        self._adaptador = adaptador

    def lancar(self, playwright):
        """Um Chromium novo — o chamador fecha ao terminar o lote."""
        return playwright.chromium.launch(headless=self._config.headless)

    def novo_contexto(self, navegador, nome_do_viewport: str):
        """Contexto com as dimensões do viewport; celular emula toque e densidade."""
        viewport = self._config.viewport(nome_do_viewport)
        opcoes = {
            "viewport": {"width": int(viewport["largura"]), "height": int(viewport["altura"])},
        }
        if viewport.get("device"):
            opcoes["is_mobile"] = True
            opcoes["has_touch"] = True
            opcoes["device_scale_factor"] = int(viewport.get("densidade", 2))
        return navegador.new_context(**opcoes)

    def nova_pagina(self, contexto, erros_de_console: list):
        """Página com coleta de erros de console e timeout padrão do projeto."""
        pagina = contexto.new_page()
        pagina.set_default_timeout(self._config.timeout_ms)
        pagina.on("console", lambda mensagem: self._anotar_erro(mensagem, erros_de_console))
        pagina.on("pageerror", lambda erro: erros_de_console.append(str(erro)[:300]))
        return pagina

    def entrar(self, contexto, pagina, perfil: str) -> bool:
        """Troca a sessão do contexto para a do perfil (visitante = sem sessão)."""
        return bool(self._adaptador.entrar_no_navegador(contexto, pagina, perfil))

    def ir(self, pagina, rota: str) -> None:
        """Abre a rota na aplicação e espera a tela assentar."""
        destino = rota
        if not rota.startswith("http"):
            destino = self._config.url_app + rota
        pagina.goto(
            destino, wait_until="domcontentloaded", timeout=self._config.timeout_de_navegacao_ms
        )
        self.assentar(pagina)

    def assentar(self, pagina) -> None:
        """Espera URL estável e texto firme, dentro do limite do projeto.

        Para quando a URL não mudou entre duas leituras e o texto passou do
        mínimo — ou, em tela legitimamente curta, quando o tamanho do texto se
        repetiu três vezes seguidas.
        """
        try:
            pagina.wait_for_load_state("networkidle", timeout=self._config.timeout_ms)
        except Exception:
            pass
        url_anterior = pagina.url
        tamanho_anterior = -1
        repeticoes = 0
        tentativa = 0
        while tentativa < self._config.tentativas_de_assentamento:
            tentativa = tentativa + 1
            pagina.wait_for_timeout(self._config.intervalo_de_assentamento_ms)
            url_atual = pagina.url
            url_estavel = url_atual == url_anterior
            url_anterior = url_atual
            if not url_estavel:
                repeticoes = 0
                continue
            tamanho = self._tamanho_do_texto(pagina)
            if tamanho >= self._config.texto_minimo_renderizado:
                return
            if tamanho > 0 and tamanho == tamanho_anterior:
                repeticoes = repeticoes + 1
            else:
                repeticoes = 0
            tamanho_anterior = tamanho
            if repeticoes >= 2:
                return

    def medir(self, pagina) -> dict:
        """O que a auditoria precisa saber sem abrir a imagem."""
        medida = {
            "url": pagina.url,
            "titulo_da_pagina": "",
            "texto_renderizado": 0,
            "scrollWidth": 0,
            "innerWidth": 0,
            "scroll_horizontal": False,
        }
        try:
            medida["titulo_da_pagina"] = pagina.title()
            medida["texto_renderizado"] = self._tamanho_do_texto(pagina)
            medida["scrollWidth"] = pagina.evaluate("document.documentElement.scrollWidth")
            medida["innerWidth"] = pagina.evaluate("window.innerWidth")
            medida["scroll_horizontal"] = medida["scrollWidth"] > medida["innerWidth"] + 1
        except Exception as erro:
            medida["falha_ao_medir"] = str(erro)[:200]
        return medida

    ROLAGEM_PARA_CARREGAR = """async () => {
        const passo = Math.max(window.innerHeight, 400);
        let y = 0;
        let voltas = 0;
        while (y < document.documentElement.scrollHeight && voltas < 40) {
            window.scrollTo(0, y);
            await new Promise((pronto) => setTimeout(pronto, 150));
            y += passo;
            voltas += 1;
        }
        window.scrollTo(0, 0);
    }"""

    def fotografar(self, pagina, destino: Path) -> None:
        """Página inteira até a altura máxima do projeto — o retrato da base visual.

        Antes, rola a página até o fim e volta: imagem com carregamento
        preguiçoso só carrega quando entra na janela, e a captura de página
        inteira não rola sozinha. A altura é limitada porque o PNG vai inteiro,
        em base64, para o git.
        """
        destino.parent.mkdir(parents=True, exist_ok=True)
        try:
            pagina.evaluate(self.ROLAGEM_PARA_CARREGAR)
            pagina.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        try:
            largura = pagina.evaluate("document.documentElement.clientWidth")
            altura = pagina.evaluate("document.documentElement.scrollHeight")
            limite = self._config.altura_maxima_da_captura_px
            recorte = {"x": 0, "y": 0, "width": largura, "height": min(altura, limite)}
            pagina.screenshot(path=str(destino), full_page=True, clip=recorte)
        except Exception:
            pagina.screenshot(path=str(destino), full_page=False)

    def fotografar_janela(self, pagina, destino: Path) -> None:
        """O que a pessoa vê agora, na janela — a captura de cada passo de jornada."""
        destino.parent.mkdir(parents=True, exist_ok=True)
        try:
            pagina.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            pass
        pagina.screenshot(path=str(destino), full_page=False)

    def _tamanho_do_texto(self, pagina) -> int:
        try:
            return len(pagina.inner_text("body"))
        except Exception:
            return 0

    def _anotar_erro(self, mensagem, acumulador: list) -> None:
        if mensagem.type == "error":
            acumulador.append(mensagem.text[:300])
