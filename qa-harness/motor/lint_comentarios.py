"""Coletor de comentários suspeitos — insumo da etapa `/qa comentarios`.

Regra (arquivo apontado por `caminhos.convencao_de_comentarios`): o código
explica o que faz agora; a história de como chegou aqui mora no `.md`.
Changelog, decisão, fluxo e achado de QA não vivem no código.

Este coletor **não dá veredito**: junta candidatos e os classifica em
`narrativa` · `codigo-comentado` · `convencao` · `bloco-longo`. Quem julga é a IA
— distinguir data de negócio de data de changelog precisa de leitura. O que
sobrar do julgamento é warning no relatório; nunca reprova a execução.
"""

import re
from pathlib import Path

SINAIS_DE_NARRATIVA = [
    (r"\b20\d{2}-\d{2}-\d{2}\b", "data"),
    (r"\b\d{1,2}/\d{1,2}/20\d{2}\b", "data"),
    (r"\bFase\s+\d", "fase do projeto"),
    (r"\bachad[oa]s?\b", "achado de QA"),
    (r"\bregress(ão|ao)\b", "regressão"),
    (r"\bhealing\b", "healing"),
    (r"\bdescobert[oa]\b", "descoberta"),
    (r"\bdecis(ão|ao) d[oae]\b", "decisão"),
    (r"\b(pedido|requisito) d[oae]\b", "pedido"),
    (r"\bantes\s+(fazia|era|o|a|isso|ele|ela|não|nao)\b", "comparação com o passado"),
    (r"\b(saiu|saíram|virou|viraram|passou a|passaram a|deixou de|deixaram de)\b", "verbo de mudança"),
    (r"\b(divergia|quebrava|estourava|falhava|acumulava|escondia)\b", "defeito já corrigido"),
    (r"\b(primeira versão|primeira versao|versão anterior|versao anterior)\b", "versão anterior"),
]

PISTAS_DE_CODIGO = [
    r"^\s*[\w.]+\s*[:=]\s*[^\s]",
    r"^\s*(def|class|function|const|let|var|import|from|return|export|if|for|await)\b",
    r"[;{}]\s*$",
    r"^\s*[}\])],?\s*$",
    r"^\s*<[A-Za-z/]",
]

LIMITE_BLOCO_LONGO = 4

LINGUAGEM_POR_EXTENSAO = {
    ".py": "python",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "javascript", ".tsx": "javascript",
    ".css": "css", ".scss": "css",
}


class Comentario:
    """Um bloco de comentário contíguo, com o necessário para julgá-lo."""

    def __init__(self, linha: int, corpo: list, documentacao: bool) -> None:
        self.linha = linha
        self.corpo = corpo
        self.documentacao = documentacao

    @property
    def texto(self) -> str:
        return " ".join(self.corpo)


class LeitorDeComentarios:
    """Extrai comentários de linha, de bloco e de documentação de um arquivo."""

    def __init__(self, arquivo: Path) -> None:
        self._arquivo = arquivo
        self.linguagem = LINGUAGEM_POR_EXTENSAO.get(arquivo.suffix, "outro")

    def blocos(self) -> list:
        try:
            linhas = self._arquivo.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeDecodeError):
            return []
        if self.linguagem == "python":
            return self._blocos_python(linhas)
        return self._blocos_c(linhas)

    def _blocos_python(self, linhas: list) -> list:
        encontrados = []
        atual: list = []
        inicio = 0
        docstring: list = []
        inicio_docstring = 0
        dentro = False
        for numero, bruta in enumerate(linhas, 1):
            linha = bruta.strip()
            aspas = linha.count('"""') + linha.count("'''")
            if dentro:
                docstring.append(linha)
                if aspas % 2 == 1:
                    dentro = False
                    encontrados.append(Comentario(inicio_docstring, docstring, True))
                    docstring = []
                continue
            if linha.startswith(('"""', "'''")):
                if aspas == 1:
                    dentro = True
                    inicio_docstring = numero
                    docstring = [linha]
                else:
                    encontrados.append(Comentario(numero, [linha], True))
                continue
            if linha.startswith("#") and not linha.startswith("#!"):
                if not atual:
                    inicio = numero
                atual.append(linha)
                continue
            if atual:
                encontrados.append(Comentario(inicio, atual, False))
                atual = []
        if atual:
            encontrados.append(Comentario(inicio, atual, False))
        return encontrados

    def _blocos_c(self, linhas: list) -> list:
        encontrados = []
        atual: list = []
        inicio = 0
        bloco: list = []
        inicio_bloco = 0
        documentacao = False
        dentro = False
        for numero, bruta in enumerate(linhas, 1):
            linha = bruta.strip()
            if dentro:
                bloco.append(linha)
                if "*/" in linha:
                    dentro = False
                    encontrados.append(Comentario(inicio_bloco, bloco, documentacao))
                    bloco = []
                continue
            aberto = linha.startswith("/*") or linha.startswith("{/*")
            if aberto:
                documentacao = linha.startswith("/**")
                if "*/" in linha:
                    encontrados.append(Comentario(numero, [linha], documentacao))
                else:
                    dentro = True
                    inicio_bloco = numero
                    bloco = [linha]
                continue
            if linha.startswith("//"):
                if not atual:
                    inicio = numero
                atual.append(linha)
                continue
            if atual:
                encontrados.append(Comentario(inicio, atual, False))
                atual = []
        if atual:
            encontrados.append(Comentario(inicio, atual, False))
        return encontrados


class Classificador:
    """Decide se um bloco é candidato a warning, e por quê."""

    def avaliar(self, comentario: Comentario) -> dict:
        if not comentario.documentacao and self._parece_codigo(comentario):
            return {
                "categoria": "codigo-comentado",
                "motivos": ["bloco de código comentado; o histórico é do git"],
                "destino_sugerido": "remover (ou virar linha no planejamento)",
            }
        motivos = self._sinais_de_narrativa(comentario.texto)
        if motivos:
            return {
                "categoria": "narrativa",
                "motivos": motivos,
                "destino_sugerido": self._destino(motivos),
            }
        if not comentario.documentacao and len(comentario.corpo) >= LIMITE_BLOCO_LONGO:
            return {
                "categoria": "bloco-longo",
                "motivos": [str(len(comentario.corpo)) + " linhas de comentário seguidas"],
                "destino_sugerido": "spec/ (o que for conceito) — no código só a nota curta",
            }
        return {}

    def _sinais_de_narrativa(self, texto: str) -> list:
        motivos = []
        for padrao, rotulo in SINAIS_DE_NARRATIVA:
            if re.search(padrao, texto, flags=re.IGNORECASE) and rotulo not in motivos:
                motivos.append(rotulo)
        return motivos

    def _parece_codigo(self, comentario: Comentario) -> bool:
        if len(comentario.corpo) < 2:
            return False
        parecidas = 0
        for linha in comentario.corpo:
            conteudo = re.sub(r"^\s*(#|//|\*|/\*)\s?", "", linha)
            if not conteudo.strip():
                continue
            for padrao in PISTAS_DE_CODIGO:
                if re.search(padrao, conteudo):
                    parecidas = parecidas + 1
                    break
        return parecidas >= max(2, len(comentario.corpo) // 2)

    def _destino(self, motivos: list) -> str:
        texto = " ".join(motivos)
        if "achado" in texto or "healing" in texto or "regressão" in texto:
            return "relatório de QA da execução (qa-harness/relatorios/<execução>/relatorio.md)"
        if "decisão" in texto or "pedido" in texto:
            return "registro de decisões do projeto (ADR / decisões)"
        return "changelog ou documento de status do projeto"


class ConvencaoPython:
    """Python documenta com docstring: `#` acima de def/class faz papel errado."""

    def avaliar(self, linhas: list) -> list:
        achados = []
        for numero, bruta in enumerate(linhas, 1):
            linha = bruta.strip()
            if not re.match(r"^(async\s+)?(def|class)\s+[A-Za-z]", linha):
                continue
            anterior = ""
            if numero >= 2:
                anterior = linhas[numero - 2].strip()
            if not anterior.startswith("#") or re.search(r"[─=-]{4,}", anterior):
                continue
            nome = re.sub(r"^(async\s+)?(def|class)\s+", "", linha).split("(")[0].rstrip(":")
            achados.append({
                "linha": numero,
                "categoria": "convencao",
                "motivos": ["comentário '#' acima de `" + nome + "` faz papel de docstring"],
                "destino_sugerido": 'trocar por docstring """…"""',
                "trecho": [anterior, linha],
            })
        return achados


class ColetorDeComentarios:
    """Varre os alvos do config e devolve os candidatos para a IA julgar."""

    def __init__(self, config, alvos: list = None) -> None:
        self._config = config
        opcoes = config.comentarios
        self._alvos = list(alvos or opcoes["alvos"])
        self._extensoes = set(opcoes["extensoes"])
        self._ignorar = set(opcoes["ignorar"])
        self._classificador = Classificador()
        self._convencao = ConvencaoPython()

    def executar(self) -> list:
        candidatos = []
        for arquivo in self._arquivos():
            relativo = self._config.relativo(arquivo)
            leitor = LeitorDeComentarios(arquivo)
            for comentario in leitor.blocos():
                avaliacao = self._classificador.avaliar(comentario)
                if not avaliacao:
                    continue
                avaliacao["arquivo"] = relativo
                avaliacao["linha"] = comentario.linha
                avaliacao["documentacao"] = comentario.documentacao
                avaliacao["trecho"] = comentario.corpo[:6]
                candidatos.append(avaliacao)
            if leitor.linguagem == "python":
                try:
                    linhas = arquivo.read_text(encoding="utf-8-sig").splitlines()
                except (OSError, UnicodeDecodeError):
                    linhas = []
                for achado in self._convencao.avaliar(linhas):
                    achado["arquivo"] = relativo
                    candidatos.append(achado)
        candidatos.sort(key=lambda item: (item["categoria"], item["arquivo"], item["linha"]))
        return candidatos

    def _arquivos(self) -> list:
        encontrados = []
        for alvo in self._alvos:
            base = self._config.raiz_projeto / alvo
            if not base.exists():
                continue
            for caminho in sorted(base.rglob("*")):
                if not caminho.is_file() or caminho.suffix not in self._extensoes:
                    continue
                relativas = caminho.relative_to(self._config.raiz_projeto).parts
                ignorado = False
                for parte in relativas:
                    if parte in self._ignorar:
                        ignorado = True
                if not ignorado:
                    encontrados.append(caminho)
        return encontrados


def resumir(candidatos: list) -> dict:
    por_categoria: dict = {}
    for candidato in candidatos:
        categoria = candidato["categoria"]
        por_categoria[categoria] = por_categoria.get(categoria, 0) + 1
    return por_categoria
