"""Changelog de evidências — indexado por TELA, com as execuções dentro dela.

Cada caminho de imagem é uma chave estável; cada execução vira uma entrada. Tela
que não mudou registra só o hash e `identica_a`; miniatura (480px, JPEG q60) só
quando o SHA-256 muda. O `git diff` do arquivo mostra quais telas mudaram entre
execuções — regressão visual versionada sem versionar imagem.

Não compete com o `evidencias.json`: aquele é a tela de agora, inteira; este é a
linha do tempo de cada tela, em miniatura.
"""

import base64
import hashlib
import io

import yaml
from PIL import Image

from .evidencia_de_pasta import materializar_caminho

LARGURA_MINIATURA = 480
QUALIDADE_JPEG = 60

CABECALHO = (
    "# CHANGELOG de evidências — indexado por TELA (append-only, versionado no git).\n"
    "# Cada chave de `telas` é um caminho de evidência estável; dentro dela, o histórico\n"
    "# de execuções. Miniatura base64 só quando o sha256 muda (execução sem mudança\n"
    "# registra `identica_a`). Gerado pelo motor da skill /qa (python qa-harness/executar.py catalogo).\n"
)


class ChangelogDeEvidencias:
    """Anexa as imagens de uma execução ao histórico de cada tela."""

    def __init__(self, config, pasta_da_execucao) -> None:
        self._config = config
        self._pasta = pasta_da_execucao
        with open(pasta_da_execucao / "manifesto.yaml", encoding="utf-8") as arquivo:
            self._manifesto = yaml.safe_load(arquivo) or {}
        self._caminho = config.caminho("evidencias") / "CHANGELOG-EVIDENCIAS.yaml"

    def executar(self) -> int:
        changelog = self._carregar()
        execucao = str(self._manifesto.get("execucao", "?"))
        contagem = {"nova": 0, "mudou": 0, "igual": 0, "ja-registrada": 0, "ausente": 0}
        imagens = self._imagens_do_manifesto()
        for caminho_relativo in imagens:
            estado = self._registrar(changelog, caminho_relativo, imagens[caminho_relativo], execucao)
            contagem[estado] = contagem[estado] + 1
        self._gravar(changelog)
        tamanho_kb = self._caminho.stat().st_size // 1024
        print(
            "    execução " + execucao + ": " + str(len(imagens)) + " imagens — "
            + str(contagem["nova"]) + " novas, " + str(contagem["mudou"]) + " mudaram, "
            + str(contagem["igual"]) + " idênticas, " + str(contagem["ja-registrada"]) + " já registradas, "
            + str(contagem["ausente"]) + " ausentes · " + str(len(changelog["telas"]))
            + " telas no changelog (" + str(tamanho_kb) + " KB)"
        )
        return 0

    def _carregar(self) -> dict:
        if not self._caminho.exists():
            return {"telas": {}}
        with open(self._caminho, encoding="utf-8") as arquivo:
            conteudo = yaml.safe_load(arquivo) or {}
        if "telas" not in conteudo:
            return {"telas": {}}
        return conteudo

    def _imagens_do_manifesto(self) -> dict:
        """{caminho da imagem: nome do ponto que a produziu}."""
        imagens: dict = {}
        for ponto in self._manifesto.get("pontos") or []:
            for caminho in ponto.get("evidencias") or []:
                if not str(caminho).lower().endswith(".png"):
                    continue
                if caminho not in imagens:
                    imagens[caminho] = str(ponto.get("nome", ""))
        return imagens

    def _registrar(self, changelog: dict, caminho_relativo: str, contexto: str, execucao: str) -> str:
        telas = changelog["telas"]
        era_nova = caminho_relativo not in telas
        if era_nova:
            telas[caminho_relativo] = {"contexto": contexto, "execucoes": []}
        historico = telas[caminho_relativo]["execucoes"]
        for registro in historico:
            if registro.get("execucao") == execucao:
                return "ja-registrada"
        arquivo = materializar_caminho(self._config.raiz_projeto, caminho_relativo)
        if arquivo is None:
            historico.append({"execucao": execucao, "erro": "arquivo ausente no registro"})
            return "ausente"
        original = arquivo.read_bytes()
        sha256 = hashlib.sha256(original).hexdigest()
        anterior = self._ultima_com_hash(historico, sha256)
        registro = {"execucao": execucao, "sha256": sha256}
        if anterior:
            registro["identica_a"] = anterior
            historico.append(registro)
            return "igual"
        imagem = Image.open(io.BytesIO(original)).convert("RGB")
        largura, altura = imagem.size
        if largura > LARGURA_MINIATURA:
            imagem = imagem.resize((LARGURA_MINIATURA, int(altura * LARGURA_MINIATURA / largura)))
        memoria = io.BytesIO()
        imagem.save(memoria, format="JPEG", quality=QUALIDADE_JPEG)
        registro["original_px"] = str(largura) + "x" + str(altura)
        registro["original_kb"] = len(original) // 1024
        registro["miniatura_jpeg_base64"] = base64.b64encode(memoria.getvalue()).decode("ascii")
        historico.append(registro)
        if era_nova:
            return "nova"
        return "mudou"

    def _ultima_com_hash(self, historico: list, sha256: str) -> str:
        encontrada = ""
        for registro in historico:
            if registro.get("sha256") != sha256:
                continue
            if registro.get("identica_a"):
                encontrada = registro["identica_a"]
            else:
                encontrada = registro.get("execucao", "")
        return encontrada

    def _gravar(self, changelog: dict) -> None:
        self._caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(self._caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(CABECALHO)
            yaml.safe_dump(changelog, arquivo, allow_unicode=True, sort_keys=True, width=100)
