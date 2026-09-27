"""Desfaz o base64 dos `evidencias.json` e devolve os `.png` das pastas.

Quem clona recebe os `evidencias.json` e nenhuma imagem. Isto escreve os
arquivos conferindo o sha256 de cada um; com `conferir`, só verifica, sem
escrever — é a checagem antes de propor commit (0 = tudo bate).
"""

import base64
import hashlib
from pathlib import Path

from .evidencia_de_pasta import NOME_DO_ARQUIVO, LeitorDeEvidencia


class Reversao:
    """Reconstrói (ou confere) as imagens a partir dos `evidencias.json`."""

    def __init__(self, config, alvos: list, conferir: bool) -> None:
        self._config = config
        self._alvos = alvos
        self._conferir = conferir
        self._escritas = 0
        self._ja_em_disco = 0
        self._problemas: list = []

    def executar(self) -> int:
        arquivos = self._arquivos_de_evidencia()
        if not arquivos:
            print("nenhum evidencias.json encontrado nos caminhos informados")
            return 0
        for arquivo in arquivos:
            self._reverter_pasta(arquivo.parent)
        self._conferir_pngs_orfaos()
        return self._relatorio(len(arquivos))

    def _arquivos_de_evidencia(self) -> list:
        encontrados = []
        for alvo in self._alvos:
            alvo = Path(alvo).resolve()
            if alvo.is_file() and alvo.name == NOME_DO_ARQUIVO:
                encontrados.append(alvo)
                continue
            if alvo.is_dir():
                for arquivo in sorted(alvo.rglob(NOME_DO_ARQUIVO)):
                    encontrados.append(arquivo)
        return encontrados

    def _reverter_pasta(self, pasta: Path) -> None:
        relativo = self._config.relativo(pasta)
        for nome, dados in LeitorDeEvidencia(pasta).imagens().items():
            codificado = dados.get("base64")
            if not codificado:
                self._problemas.append(relativo + "/" + nome + ": sem base64 no JSON")
                continue
            bruto = base64.b64decode(codificado)
            esperado = dados.get("sha256")
            if esperado and hashlib.sha256(bruto).hexdigest() != esperado:
                self._problemas.append(relativo + "/" + nome + ": sha256 do base64 não bate com o declarado")
                continue
            destino = pasta / nome
            if destino.exists():
                self._ja_em_disco = self._ja_em_disco + 1
                if esperado and hashlib.sha256(destino.read_bytes()).hexdigest() != esperado:
                    self._problemas.append(relativo + "/" + nome + ": imagem em disco difere do base64 versionado")
                continue
            if self._conferir:
                self._problemas.append(relativo + "/" + nome + ": ausente em disco")
                continue
            destino.write_bytes(bruto)
            self._escritas = self._escritas + 1

    def _conferir_pngs_orfaos(self) -> None:
        """`.png` em pasta sem `evidencias.json`, ou fora dele, fere o contrato."""
        for alvo in self._alvos:
            alvo = Path(alvo).resolve()
            if not alvo.is_dir():
                continue
            for imagem in sorted(alvo.rglob("*.png")):
                registradas = LeitorDeEvidencia(imagem.parent).imagens()
                if imagem.name not in registradas:
                    self._problemas.append(self._config.relativo(imagem) + ": .png sem entrada no evidencias.json")
                irmao = imagem.with_suffix(".json")
                if irmao.exists():
                    self._problemas.append(self._config.relativo(irmao) + ": .json por imagem (formato antigo)")

    def _relatorio(self, pastas: int) -> int:
        acao = "conferidas" if self._conferir else "escritas"
        print(str(pastas) + " pasta(s) com evidencias.json")
        print("  imagens " + acao + ": " + str(self._escritas))
        print("  já estavam em disco: " + str(self._ja_em_disco))
        if not self._problemas:
            print("  íntegro: todo sha256 confere")
            return 0
        print("  " + str(len(self._problemas)) + " problema(s):")
        for problema in self._problemas:
            print("    - " + problema)
        return 2
