"""Um `evidencias.json` por pasta de imagens, com o PNG cru em base64.

O `.png` fica só em disco (fora do git); o `evidencias.json` é a cópia
versionada: chaveado pelo nome da imagem, traz as métricas da captura e a
imagem inteira em base64, sem perda, com `sha256` e `bytes`. Quem clona devolve
os `.png` com `python qa-harness/executar.py reverter`.

Vale para pasta com imagem (`_base/`, `jornadas/`, `_olhar/`). `api/` guarda um
JSON por chamada, sem imagem, e não passa por aqui.
"""

import base64
import hashlib
import json
from pathlib import Path

NOME_DO_ARQUIVO = "evidencias.json"


class EvidenciaDePasta:
    """Acumula as telas de uma pasta e grava o `evidencias.json` dela.

    Uso:
        pasta = EvidenciaDePasta(caminho, raiz_projeto, gerado_por="jornadas")
        pasta.registrar("01-painel.png", {"url": ..., "marco": "INICIO"})
        pasta.gravar()
    """

    def __init__(
        self, caminho: Path, raiz_projeto: Path, gerado_por: str, extra: dict = None
    ) -> None:
        self._caminho = Path(caminho).resolve()
        self._raiz_projeto = Path(raiz_projeto).resolve()
        self._gerado_por = gerado_por
        self._extra = dict(extra or {})
        self._telas: dict = {}

    def registrar(self, nome_da_imagem: str, metricas: dict) -> None:
        """Guarda as métricas de uma tela; o base64 é lido na hora de gravar."""
        self._telas[nome_da_imagem] = dict(metricas)

    def anotar(self, chave: str, valor) -> None:
        """Acrescenta um dado ao cabeçalho do arquivo (veredito, passos...)."""
        self._extra[chave] = valor

    def gravar(self):
        """Escreve o `evidencias.json`. Sem tela registrada, não grava nada."""
        if not self._telas:
            return None
        imagens = {}
        for nome in sorted(self._telas):
            imagens[nome] = self._montar_entrada(nome, self._telas[nome])
        relativo = self._caminho.relative_to(self._raiz_projeto).as_posix()
        conteudo = {
            "pasta": relativo,
            "gerado_por": self._gerado_por,
            "formato": "png",
            "telas": len(imagens),
            "como_reverter": "python qa-harness/executar.py reverter " + relativo,
        }
        for chave in self._extra:
            conteudo[chave] = self._extra[chave]
        conteudo["imagens"] = imagens
        destino = self._caminho / NOME_DO_ARQUIVO
        destino.parent.mkdir(parents=True, exist_ok=True)
        with open(destino, "w", encoding="utf-8") as arquivo:
            json.dump(conteudo, arquivo, ensure_ascii=False, indent=2, default=str)
        return destino

    def _montar_entrada(self, nome: str, metricas: dict) -> dict:
        """Métricas primeiro, base64 por último — o diff começa legível."""
        entrada = dict(metricas)
        imagem = self._caminho / nome
        if not imagem.exists():
            entrada["ausente"] = "imagem não encontrada em disco ao gravar o JSON"
            return entrada
        bruto = imagem.read_bytes()
        entrada["bytes"] = len(bruto)
        entrada["sha256"] = hashlib.sha256(bruto).hexdigest()
        entrada["base64"] = base64.b64encode(bruto).decode("ascii")
        return entrada


class LeitorDeEvidencia:
    """Lê o `evidencias.json` de uma pasta — para o PDF, o lint e a reversão."""

    def __init__(self, pasta: Path) -> None:
        self._pasta = Path(pasta).resolve()

    @property
    def pasta(self) -> Path:
        return self._pasta

    def existe(self) -> bool:
        return (self._pasta / NOME_DO_ARQUIVO).exists()

    def conteudo(self) -> dict:
        """O arquivo inteiro, ou vazio se não existir ou estiver corrompido."""
        caminho = self._pasta / NOME_DO_ARQUIVO
        if not caminho.exists():
            return {}
        try:
            return json.loads(caminho.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def imagens(self) -> dict:
        """Mapa {nome_da_imagem: metadados}."""
        return self.conteudo().get("imagens") or {}

    def materializar(self, nome: str):
        """Garante a imagem em disco: usa a que já existe ou desfaz o base64.

        É o que deixa o PDF sair com as imagens num clone sem nenhum `.png`.
        """
        destino = self._pasta / nome
        if destino.exists():
            return destino
        dados = self.imagens().get(nome) or {}
        codificado = dados.get("base64")
        if not codificado:
            return None
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(base64.b64decode(codificado))
        return destino


def materializar_caminho(raiz_projeto: Path, caminho_relativo: str):
    """Atalho: devolve o `.png` em disco a partir do caminho relativo dele."""
    absoluto = Path(raiz_projeto) / caminho_relativo
    if absoluto.exists():
        return absoluto
    return LeitorDeEvidencia(absoluto.parent).materializar(absoluto.name)


def limpar_pasta_de_imagens(pasta: Path) -> None:
    """Apaga `.png` e `.json` da pasta antes de uma nova captura.

    Reexecução reescreve a pasta inteira: tela renomeada no catálogo não pode
    sobreviver ao lado da nova.
    """
    if not pasta.exists():
        return
    for arquivo in pasta.iterdir():
        if arquivo.is_file() and arquivo.suffix in (".png", ".json"):
            arquivo.unlink()
