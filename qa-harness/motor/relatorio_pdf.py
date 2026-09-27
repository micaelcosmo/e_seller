"""Relatório em PDF — um documento por história de usuário.

Escrito para quem não acompanhou a execução: abre com a história e os critérios
de aceite, mostra o que foi verificado e só então a prova — o caminho percorrido
tela a tela, do INÍCIO ao FIM, com a legenda de cada passo acima da imagem.

Nada é redigido livremente: o texto vem de `spec/test/historias/` e
`spec/test/planos/`; o resultado vem do `manifesto.yaml`. As imagens saem do
disco ou, num clone sem `.png`, do base64 do `evidencias.json` da pasta.
"""

import io
import re
import shutil
import unicodedata
from pathlib import Path

import yaml
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image

from .especificacao import Especificacao
from .evidencia_de_pasta import materializar_caminho


class DocumentoDeQualidade(FPDF):
    """PDF com rodapé numerado."""

    def __init__(self, titulo_do_rodape: str) -> None:
        super().__init__()
        self._titulo_do_rodape = titulo_do_rodape

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font(self.font_family, "", 7)
        self.set_text_color(130, 130, 130)
        self.cell(0, 5, self._titulo_do_rodape + "   |   página " + str(self.page_no()), align="C")
        self.set_text_color(0, 0, 0)


class RelatorioEmPdf:
    """Gera um PDF por história a partir do manifesto da execução."""

    LARGURA_UTIL = 180
    LARGURA_DA_IMAGEM_NO_PDF = 1400
    ALTURA_MAXIMA_DA_IMAGEM_MM = 205

    COR_VALIDO = (22, 122, 60)
    COR_FALHA = (176, 30, 58)
    COR_ATENCAO = (200, 120, 20)
    COR_NEUTRA = (110, 110, 110)

    CORES_POR_VEREDITO = {
        "VALIDO": COR_VALIDO,
        "FALHA DE PRODUTO": COR_FALHA,
        "EVIDENCIA INVALIDA": COR_ATENCAO,
        "INCONCLUSIVO": COR_NEUTRA,
    }

    ORDEM_DAS_SUITES = {"integracao": 0, "jornada": 1, "base": 2}

    FONTES_CANDIDATAS = [
        ("Arial", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf",
         "C:/Windows/Fonts/ariali.ttf"),
        ("Arial", "/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "/System/Library/Fonts/Supplemental/Arial Italic.ttf"),
        ("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
    ]

    def __init__(self, config, pasta_da_execucao: Path) -> None:
        self._config = config
        self._spec = Especificacao(config)
        self._pasta = Path(pasta_da_execucao)
        with open(self._pasta / "manifesto.yaml", encoding="utf-8") as arquivo:
            self._manifesto = yaml.safe_load(arquivo) or {}
        self._destino = self._pasta / "pdf"
        self._familia = "Helvetica"
        self._tem_acentuacao = False

    def executar(self) -> int:
        """Agrupa os pontos por história e gera um documento para cada uma."""
        if self._destino.exists():
            shutil.rmtree(self._destino)
        self._destino.mkdir(parents=True, exist_ok=True)
        grupos = self._agrupar_por_historia()
        for chave in grupos:
            self._gerar_um(chave[0], chave[1], grupos[chave])
        print(
            "    " + str(len(grupos)) + " PDF(s) em " + self._config.relativo(self._destino)
            + " (acentuação: " + ("sim" if self._tem_acentuacao else "não") + ")"
        )
        return 0

    # ── documento ────────────────────────────────────────────────────────

    def _gerar_um(self, dominio: str, nome_da_historia: str, pontos: list) -> None:
        historia = self._spec.historia(nome_da_historia)
        documento = DocumentoDeQualidade(self._ascii(nome_da_historia))
        self._registrar_fonte(documento)
        documento.set_auto_page_break(auto=True, margin=20)
        documento.add_page()
        self._capa(documento, dominio, nome_da_historia, pontos)
        self._historia_de_usuario(documento, dominio, historia)
        self._criterios(documento, dominio, historia)
        self._resumo_dos_pontos(documento, pontos)
        self._detalhamento(documento, pontos)
        self._achados(documento, pontos)
        nome = self._nome_de_arquivo(dominio, nome_da_historia)
        documento.output(str(self._destino / nome))

    def _capa(self, documento, dominio, nome_da_historia, pontos) -> None:
        self._rotulo_pequeno(documento, "RELATÓRIO DE QUALIDADE")
        documento.set_font(self._familia, "B", 17)
        self._paragrafo(documento, nome_da_historia, altura=8)
        documento.ln(1)
        documento.set_font(self._familia, "", 9)
        documento.set_text_color(*self.COR_NEUTRA)
        identificacao = (
            "Projeto " + str(self._manifesto.get("projeto", ""))
            + "   |   Domínio: " + dominio
            + "   |   Execução: " + str(self._manifesto.get("execucao", ""))
            + "   |   Modo: " + str(self._manifesto.get("modo", ""))
            + "   |   Branch: " + str(self._manifesto.get("branch", ""))
        )
        self._paragrafo(documento, identificacao, altura=5)
        documento.set_text_color(0, 0, 0)
        documento.ln(3)
        self._faixa_de_resultado(documento, pontos)
        if not self._manifesto.get("revisao"):
            documento.ln(1)
            documento.set_font(self._familia, "I", 8)
            documento.set_text_color(*self.COR_ATENCAO)
            self._paragrafo(
                documento,
                "Revisão de validade pendente: vereditos automáticos do motor, ainda sem a leitura das evidências.",
                altura=4,
            )
            documento.set_text_color(0, 0, 0)
        documento.ln(4)

    def _faixa_de_resultado(self, documento, pontos: list) -> None:
        falhas = self._com_veredito(pontos, "FALHA DE PRODUTO")
        duvidosos = self._com_veredito(pontos, "EVIDENCIA INVALIDA") + self._com_veredito(pontos, "INCONCLUSIVO")
        if falhas:
            cor = self.COR_FALHA
            texto = "REPROVADO - " + str(len(falhas)) + " falha(s) de produto em " + str(len(pontos)) + " verificação(ões)"
        elif duvidosos:
            cor = self.COR_ATENCAO
            texto = "INCONCLUSIVO - evidência insuficiente em " + str(len(duvidosos)) + " verificação(ões)"
        else:
            cor = self.COR_VALIDO
            texto = "APROVADO - " + str(len(pontos)) + " verificação(ões), todas com evidência válida"
        documento.set_fill_color(cor[0], cor[1], cor[2])
        documento.set_text_color(255, 255, 255)
        documento.set_font(self._familia, "B", 11)
        documento.cell(self.LARGURA_UTIL, 9, "  " + self._texto(texto), fill=True,
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        documento.set_text_color(0, 0, 0)

    def _historia_de_usuario(self, documento, dominio, historia) -> None:
        self._titulo_de_secao(documento, "1. História de usuário")
        if dominio == "base-visual":
            documento.set_font(self._familia, "", 10)
            self._paragrafo(
                documento,
                "Retrato do sistema, tela a tela, independente de história: é o que revela "
                "quebra em tela que nenhuma jornada cobre e serve de linha de base da regressão visual. "
                "Catálogo: " + self._config.relativo(self._config.caminho("base_visual")) + ".",
            )
            documento.ln(3)
            return
        if historia is None or not historia.narrativa:
            documento.set_font(self._familia, "I", 10)
            self._paragrafo(documento, "História não encontrada em spec/test/historias/ — lacuna de especificação.")
            documento.ln(3)
            return
        documento.set_font(self._familia, "", 11)
        self._paragrafo(documento, historia.narrativa, altura=6)
        documento.ln(2)
        if historia.fontes:
            documento.set_font(self._familia, "I", 8)
            documento.set_text_color(*self.COR_NEUTRA)
            self._paragrafo(documento, "Derivada de: " + historia.fontes, altura=4)
            documento.set_text_color(0, 0, 0)
        documento.ln(3)

    def _criterios(self, documento, dominio, historia) -> None:
        if dominio == "base-visual":
            return
        self._titulo_de_secao(documento, "2. Critérios de aceite")
        if historia is None or not historia.criterios:
            documento.set_font(self._familia, "I", 10)
            self._paragrafo(documento, "Nenhum critério declarado para esta história.")
            documento.ln(3)
            return
        for criterio in historia.criterios:
            self._item_de_lista(documento, criterio)
        documento.ln(3)

    def _resumo_dos_pontos(self, documento, pontos: list) -> None:
        self._titulo_de_secao(documento, "3. Verificações realizadas")
        documento.set_font(self._familia, "B", 8)
        documento.set_fill_color(238, 238, 238)
        documento.cell(120, 7, "  Verificação", fill=True)
        documento.cell(24, 7, "Suíte", fill=True)
        documento.cell(36, 7, "Resultado", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        documento.set_font(self._familia, "", 8)
        for ponto in pontos:
            cor = self.CORES_POR_VEREDITO.get(ponto.get("veredito"), (0, 0, 0))
            documento.cell(120, 6, "  " + self._texto(self._encurtar(str(ponto.get("nome", "")), 68)))
            documento.cell(24, 6, self._texto(str(ponto.get("suite", ""))))
            documento.set_text_color(cor[0], cor[1], cor[2])
            documento.set_font(self._familia, "B", 8)
            documento.cell(36, 6, self._texto(str(ponto.get("veredito", ""))), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            documento.set_text_color(0, 0, 0)
            documento.set_font(self._familia, "", 8)
        documento.ln(4)

    def _detalhamento(self, documento, pontos: list) -> None:
        self._titulo_de_secao(documento, "4. Detalhamento e evidências")
        for ponto in pontos:
            self._ponto(documento, ponto)

    def _ponto(self, documento, ponto: dict) -> None:
        documento.ln(2)
        documento.set_font(self._familia, "B", 11)
        self._paragrafo(documento, self._texto(str(ponto.get("nome", ""))), altura=6)
        cor = self.CORES_POR_VEREDITO.get(ponto.get("veredito"), (0, 0, 0))
        documento.set_font(self._familia, "B", 9)
        documento.set_text_color(cor[0], cor[1], cor[2])
        linha = str(ponto.get("veredito")) + "   |   suíte " + str(ponto.get("suite"))
        if ponto.get("viewport"):
            linha = linha + "   |   " + str(ponto["viewport"])
        if ponto.get("ciclos_de_healing"):
            linha = linha + "   |   " + str(ponto["ciclos_de_healing"]) + " ciclo(s) de healing no teste"
        self._paragrafo(documento, linha, altura=5)
        documento.set_text_color(0, 0, 0)
        documento.ln(1)

        plano = self._spec.ponto(str(ponto.get("nome", "")), str(ponto.get("dominio", "")))
        if plano is not None and plano.validade:
            self._bloco_rotulado(documento, "Critério de validade", plano.validade)
        if plano is not None and plano.pre_condicoes:
            condicoes = []
            for item in plano.pre_condicoes:
                condicoes.append(str(item))
            self._bloco_rotulado(documento, "Pré-condições", "; ".join(condicoes))
        self._bloco_rotulado(documento, "Leitura da evidência", str(ponto.get("detalhe", "")))
        automatico = ponto.get("veredito_automatico")
        if automatico and automatico != ponto.get("veredito"):
            self._bloco_rotulado(documento, "Veredito do motor antes da revisão", str(automatico))
        if ponto.get("revisao_motivo"):
            self._bloco_rotulado(documento, "Revisão de validade", str(ponto["revisao_motivo"]))

        percurso = ponto.get("percurso") or []
        if percurso:
            self._percurso(documento, percurso, str(ponto.get("suite")))
        else:
            self._evidencias_de_dados(documento, ponto.get("evidencias") or [])
        documento.ln(3)

    def _percurso(self, documento, percurso: list, suite: str) -> None:
        documento.ln(1)
        rotulo = "TELAS CAPTURADAS" if suite == "base" else "CAMINHO PERCORRIDO"
        self._rotulo_pequeno(documento, rotulo)
        total = len(percurso)
        for passo in percurso:
            self._passo(documento, passo, total)

    def _passo(self, documento, passo: dict, total: int) -> None:
        captura = str(passo.get("captura", ""))
        imagem = materializar_caminho(self._config.raiz_projeto, captura) if captura else None
        if documento.get_y() + self._altura_estimada(imagem) + 24 > documento.h - 20:
            documento.add_page()
        documento.ln(2)
        marco = str(passo.get("marco", "passo"))
        cor = self.COR_NEUTRA
        if marco == "INICIO":
            cor = self.COR_VALIDO
        elif marco == "FIM":
            cor = self.COR_FALHA
        documento.set_font(self._familia, "B", 9)
        documento.set_text_color(cor[0], cor[1], cor[2])
        cabecalho = "PASSO " + str(passo.get("ordem")) + " DE " + str(total)
        if marco in ("INICIO", "FIM"):
            cabecalho = cabecalho + "  -  " + marco
        documento.cell(self.LARGURA_UTIL, 5, self._texto(cabecalho), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        documento.set_text_color(0, 0, 0)
        documento.set_font(self._familia, "", 10)
        self._paragrafo(documento, self._texto(str(passo.get("rotulo", ""))), altura=5)
        observado = passo.get("observado") or {}
        if observado.get("erro"):
            documento.set_font(self._familia, "I", 8)
            documento.set_text_color(*self.COR_FALHA)
            self._paragrafo(documento, self._texto("Não confirmado: " + str(observado["erro"])), altura=4)
            documento.set_text_color(0, 0, 0)
        documento.set_font("Courier", "", 6)
        documento.set_text_color(150, 150, 150)
        self._paragrafo(documento, self._ascii(captura), altura=3)
        documento.set_text_color(0, 0, 0)
        documento.ln(1)
        self._embutir_imagem(documento, imagem)

    def _evidencias_de_dados(self, documento, evidencias: list) -> None:
        if not evidencias:
            return
        documento.ln(1)
        self._rotulo_pequeno(documento, "EVIDÊNCIAS REGISTRADAS")
        documento.set_font("Courier", "", 7)
        documento.set_text_color(110, 110, 110)
        for caminho in evidencias:
            self._paragrafo(documento, self._ascii(str(caminho)), altura=4)
        documento.set_text_color(0, 0, 0)

    def _achados(self, documento, pontos: list) -> None:
        falhas = self._com_veredito(pontos, "FALHA DE PRODUTO")
        if not falhas:
            return
        documento.add_page()
        self._titulo_de_secao(documento, "5. Ajuste / retorno para o desenvolvimento")
        numero = 0
        for ponto in falhas:
            numero = numero + 1
            documento.set_font(self._familia, "B", 11)
            documento.set_text_color(*self.COR_FALHA)
            self._paragrafo(
                documento,
                self._texto("Achado " + str(numero) + " - " + str(ponto.get("nome", "")).split(" - ", 1)[-1]),
                altura=6,
            )
            documento.set_text_color(0, 0, 0)
            self._bloco_rotulado(documento, "O que a evidência mostra", str(ponto.get("detalhe", "")))
            plano = self._spec.ponto(str(ponto.get("nome", "")), str(ponto.get("dominio", "")))
            if plano is not None and plano.validade:
                self._bloco_rotulado(documento, "Critério que deveria ter sido atendido", plano.validade)
            documento.ln(3)

    # ── blocos básicos ───────────────────────────────────────────────────

    def _titulo_de_secao(self, documento, titulo: str) -> None:
        documento.ln(3)
        documento.set_font(self._familia, "B", 12)
        documento.cell(self.LARGURA_UTIL, 7, self._texto(titulo), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        documento.set_draw_color(210, 210, 210)
        documento.line(documento.l_margin, documento.get_y(), documento.l_margin + self.LARGURA_UTIL, documento.get_y())
        documento.ln(2)

    def _rotulo_pequeno(self, documento, texto: str) -> None:
        documento.set_font(self._familia, "B", 7)
        documento.set_text_color(*self.COR_NEUTRA)
        documento.cell(self.LARGURA_UTIL, 4, self._texto(texto), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        documento.set_text_color(0, 0, 0)

    def _bloco_rotulado(self, documento, rotulo: str, conteudo: str) -> None:
        if not conteudo:
            return
        documento.ln(1)
        self._rotulo_pequeno(documento, rotulo.upper())
        documento.set_font(self._familia, "", 9)
        self._paragrafo(documento, self._texto(" ".join(str(conteudo).split())), altura=5)

    def _item_de_lista(self, documento, texto: str) -> None:
        documento.set_font(self._familia, "", 10)
        documento.cell(5, 5, "-")
        anterior = documento.l_margin
        documento.set_left_margin(anterior + 5)
        documento.set_x(anterior + 5)
        documento.multi_cell(self.LARGURA_UTIL - 5, 5, self._texto(texto), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        documento.set_left_margin(anterior)
        documento.set_x(anterior)

    def _paragrafo(self, documento, texto: str, altura: int = 5) -> None:
        """Parágrafo que sempre volta à margem esquerda (padrão do fpdf2 é seguir à direita)."""
        documento.multi_cell(self.LARGURA_UTIL, altura, str(texto), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── imagens ──────────────────────────────────────────────────────────

    def _embutir_imagem(self, documento, imagem) -> None:
        if imagem is None:
            documento.set_font(self._familia, "I", 8)
            self._paragrafo(documento, "[captura ausente em disco e no evidencias.json]", altura=4)
            return
        try:
            reduzida, largura, altura, recortada = self._reduzida(imagem)
            documento.image(reduzida, w=largura, h=altura)
            documento.ln(2)
            if recortada:
                documento.set_font(self._familia, "I", 7)
                documento.set_text_color(150, 150, 150)
                self._paragrafo(
                    documento,
                    self._texto("Captura recortada no topo para caber na página; o arquivo completo está no caminho acima."),
                    altura=4,
                )
                documento.set_text_color(0, 0, 0)
        except Exception as erro:
            documento.set_font(self._familia, "I", 8)
            self._paragrafo(documento, "[captura não pôde ser embutida: " + str(erro)[:80] + "]", altura=4)

    def _reduzida(self, caminho: Path):
        """Largura cheia da página; o que não cabe em altura é recortado no topo."""
        with Image.open(caminho) as imagem:
            copia = imagem.convert("RGB")
            proporcao_maxima = self.ALTURA_MAXIMA_DA_IMAGEM_MM / float(self.LARGURA_UTIL)
            altura_maxima = int(copia.width * proporcao_maxima)
            recortada = False
            if copia.height > altura_maxima:
                copia = copia.crop((0, 0, copia.width, altura_maxima))
                recortada = True
            if copia.width > self.LARGURA_DA_IMAGEM_NO_PDF:
                fator = self.LARGURA_DA_IMAGEM_NO_PDF / float(copia.width)
                copia = copia.resize((self.LARGURA_DA_IMAGEM_NO_PDF, int(copia.height * fator)))
            proporcao = copia.height / float(copia.width)
            memoria = io.BytesIO()
            copia.save(memoria, format="JPEG", quality=72, optimize=True)
        memoria.seek(0)
        return memoria, self.LARGURA_UTIL, self.LARGURA_UTIL * proporcao, recortada

    def _altura_estimada(self, imagem) -> float:
        if imagem is None:
            return 0.0
        try:
            with Image.open(imagem) as aberta:
                proporcao = aberta.height / float(aberta.width)
        except Exception:
            return 0.0
        return min(self.LARGURA_UTIL * proporcao, self.ALTURA_MAXIMA_DA_IMAGEM_MM)

    # ── apoio ────────────────────────────────────────────────────────────

    def _registrar_fonte(self, documento) -> None:
        for candidata in self.FONTES_CANDIDATAS:
            regular = Path(candidata[1])
            if not regular.exists():
                continue
            documento.add_font(candidata[0], "", str(regular))
            if Path(candidata[2]).exists():
                documento.add_font(candidata[0], "B", str(candidata[2]))
            if Path(candidata[3]).exists():
                documento.add_font(candidata[0], "I", str(candidata[3]))
            self._familia = candidata[0]
            self._tem_acentuacao = True
            return
        self._familia = "Helvetica"
        self._tem_acentuacao = False

    def _texto(self, valor: str) -> str:
        if self._tem_acentuacao:
            return str(valor)
        return self._ascii(valor)

    def _agrupar_por_historia(self) -> dict:
        """{(dominio, historia): [pontos]} — integração, depois jornada, depois base."""
        grupos: dict = {}
        for ponto in self._manifesto.get("pontos") or []:
            chave = (str(ponto.get("dominio", "")), str(ponto.get("historia", "")))
            if chave not in grupos:
                grupos[chave] = []
            grupos[chave].append(ponto)
        for chave in grupos:
            grupos[chave].sort(key=self._ordem_do_ponto)
        return grupos

    def _ordem_do_ponto(self, ponto: dict):
        return (self.ORDEM_DAS_SUITES.get(str(ponto.get("suite")), 9), str(ponto.get("nome", "")))

    def _com_veredito(self, pontos: list, veredito: str) -> list:
        encontrados = []
        for ponto in pontos:
            if ponto.get("veredito") == veredito:
                encontrados.append(ponto)
        return encontrados

    def _encurtar(self, texto: str, limite: int) -> str:
        if len(texto) <= limite:
            return texto
        return texto[: limite - 3] + "..."

    def _nome_de_arquivo(self, dominio: str, historia: str) -> str:
        simples = self._ascii(dominio + "-" + historia).lower().replace(" - ", "-")
        simples = re.sub(r"[^a-z0-9]+", "-", simples).strip("-")
        return simples[:120] + ".pdf"

    def _ascii(self, texto: str) -> str:
        normalizado = unicodedata.normalize("NFKD", str(texto))
        return normalizado.encode("ascii", "ignore").decode("ascii")
