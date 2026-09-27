"""Sobe, derruba e informa a stack de QA do e_seller — sempre em portas livres.

    python qa-harness/ambiente/stack.py subir    # confere as portas, sobe (com build) e espera o app
    python qa-harness/ambiente/stack.py descer   # para os containers (mantém banco e arquivos)
    python qa-harness/ambiente/stack.py zerar    # para e apaga os volumes de QA
    python qa-harness/ambiente/stack.py estado   # portas, containers e saúde

Portas: a fonte é o `qa-harness/config.yaml` (`urls.app` = frontend, `ambiente.backend`
e `ambiente.banco_porta`). Antes de subir, cada porta é conferida; se outro processo
a ocupa (aceita conexão ou aparece em LISTENING no netstat) e não é a própria stack
de QA, a próxima porta livre da faixa é escolhida e o config.yaml é reescrito — o
diff mostra a troca. As faixas ficam longe das portas de dev (48080/48173/48432/48088).

Credenciais: aleatórias, geradas na primeira subida em `credenciais-locais.env`,
fora do git (ver credenciais.py). Nenhum valor é impresso.
"""

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

import requests
import yaml

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA.parent))

from ambiente.credenciais import CredenciaisLocais  # noqa: E402


class VerificadorDePortas:
    """Descobre se uma porta do host está livre para a stack de QA."""

    def __init__(self, portas_da_propria_stack: set) -> None:
        """Recebe as portas já publicadas pela stack de QA (contam como livres)."""
        self.portas_da_propria_stack = portas_da_propria_stack
        self.portas_em_escuta = self._portas_em_escuta()

    def _portas_em_escuta(self) -> set:
        """Portas TCP em LISTENING segundo o netstat (pega o que não aceita conexão)."""
        encontradas = set()
        for protocolo in ("tcp", "tcpv6"):
            for linha in self._netstat(protocolo).splitlines():
                partes = linha.split()
                if len(partes) < 4 or partes[3].upper() not in ("LISTENING", "ESCUTANDO"):
                    continue
                final = partes[1].rsplit(":", 1)[-1]
                if final.isdigit():
                    encontradas.add(int(final))
        return encontradas

    def _netstat(self, protocolo: str) -> str:
        """Saída do netstat do Windows; vazia em sistema sem ele."""
        try:
            resultado = subprocess.run(
                ["netstat", "-ano", "-p", protocolo], capture_output=True, text=True, timeout=30
            )
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return resultado.stdout

    def _aceita_conexao(self, porta: int) -> bool:
        """Algum processo aceita conexão na porta (IPv4 ou IPv6 local)?"""
        for host, familia in (("127.0.0.1", socket.AF_INET), ("::1", socket.AF_INET6)):
            soquete = socket.socket(familia, socket.SOCK_STREAM)
            soquete.settimeout(0.5)
            try:
                if soquete.connect_ex((host, porta)) == 0:
                    return True
            except OSError:
                pass
            finally:
                soquete.close()
        return False

    def livre(self, porta: int) -> bool:
        """Livre = ninguém usa, ou quem usa é a própria stack de QA."""
        if porta in self.portas_da_propria_stack:
            return True
        return porta not in self.portas_em_escuta and not self._aceita_conexao(porta)

    def escolher(self, preferida: int, faixa: range, reservadas: set) -> int:
        """A porta do config quando está livre; senão, a primeira livre da faixa."""
        if preferida not in reservadas and self.livre(preferida):
            return preferida
        for candidata in faixa:
            if candidata in reservadas:
                continue
            if self.livre(candidata):
                return candidata
        raise RuntimeError("nenhuma porta livre na faixa " + str(faixa.start) + "-" + str(faixa.stop - 1))


class StackDeQa:
    """Orquestra o docker compose da stack de QA (projeto `eseller-qa`)."""

    PROJETO_COMPOSE = "eseller-qa"
    FAIXA_FRONTEND = range(48270, 48280)
    FAIXA_BACKEND = range(48280, 48290)
    FAIXA_BANCO = range(48530, 48540)
    ESPERA_EM_SEGUNDOS = 420
    PADRAO_PORTA_DO_BANCO = re.compile(r"^(\s*banco_porta:\s*)(\d+)(.*)$", re.M)

    def __init__(self, pasta: Path) -> None:
        """Resolve os caminhos da stack a partir da pasta `qa-harness/ambiente/`."""
        self.pasta = pasta
        self.arquivo_compose = pasta / "docker-compose.qa.yml"
        self.arquivo_config = pasta.parent / "config.yaml"
        self.credenciais = CredenciaisLocais(pasta / "credenciais-locais.env")

    # ── configuração ─────────────────────────────────────────────────────

    def ler_config(self) -> dict:
        """O config.yaml do harness, onde moram as portas e as contas do QA."""
        with open(self.arquivo_config, encoding="utf-8") as arquivo:
            return yaml.safe_load(arquivo) or {}

    def _porta_da_url(self, url: str) -> int:
        """Porta explícita de uma URL `http://host:porta`."""
        encontrado = re.search(r":(\d+)(/|$)", str(url).replace("://", ""))
        if not encontrado:
            raise ValueError("a URL do config.yaml precisa declarar a porta: " + str(url))
        return int(encontrado.group(1))

    def portas_do_config(self, config: dict) -> dict:
        """Portas de frontend, backend e banco declaradas no config.yaml."""
        ambiente = config.get("ambiente") or {}
        return {
            "frontend": self._porta_da_url((config.get("urls") or {}).get("app", "")),
            "backend": self._porta_da_url(ambiente.get("backend", "")),
            "banco": int(ambiente.get("banco_porta", 0)),
        }

    def _reescrever_portas(self, antigas: dict, novas: dict) -> None:
        """Grava as portas escolhidas no config.yaml, preservando comentários."""
        texto = self.arquivo_config.read_text(encoding="utf-8")
        for servico in ("frontend", "backend"):
            texto = texto.replace(
                "127.0.0.1:" + str(antigas[servico]) + "\n", "127.0.0.1:" + str(novas[servico]) + "\n"
            )
            texto = texto.replace(
                "127.0.0.1:" + str(antigas[servico]) + " ", "127.0.0.1:" + str(novas[servico]) + " "
            )
        texto = self.PADRAO_PORTA_DO_BANCO.sub(r"\g<1>" + str(novas["banco"]) + r"\g<3>", texto)
        self.arquivo_config.write_text(texto, encoding="utf-8")

    def _contas_do_config(self, config: dict, credenciais: dict) -> dict:
        """Conta do admin semeada pelo próprio backend no boot (APP_ENV=dev)."""
        perfis = config.get("perfis") or {}
        admin = perfis.get("admin") or {}
        return {
            "QA_ADMIN_EMAIL": str(admin.get("conta", "")),
            "QA_ADMIN_PASSWORD": credenciais.get("QA_ADMIN_PASSWORD", ""),
        }

    def _ambiente_do_compose(self, config: dict, credenciais: dict, portas: dict) -> dict:
        """Variáveis que o docker-compose.qa.yml interpola (nada vem do .env)."""
        ambiente = dict(os.environ)
        ambiente.update(credenciais)
        ambiente.update(self._contas_do_config(config, credenciais))
        ambiente["QA_PORTA_FRONTEND"] = str(portas["frontend"])
        ambiente["QA_PORTA_BACKEND"] = str(portas["backend"])
        ambiente["QA_PORTA_BANCO"] = str(portas["banco"])
        return ambiente

    # ── docker ───────────────────────────────────────────────────────────

    def _docker(self, comando: list, ambiente: dict = None):
        """Executa um comando do docker; `None` quando o docker não está disponível."""
        try:
            return subprocess.run(
                comando,
                cwd=str(self.pasta),
                env=ambiente,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=1800,
            )
        except (OSError, subprocess.TimeoutExpired) as erro:
            print("docker indisponível: " + type(erro).__name__ + " — o Docker Desktop está aberto?")
            return None

    def _compose(self, argumentos: list) -> list:
        """Comando `docker compose` já apontado para o projeto e o arquivo da stack."""
        base = ["docker", "compose", "-p", self.PROJETO_COMPOSE, "-f", str(self.arquivo_compose)]
        for argumento in argumentos:
            base.append(argumento)
        return base

    def containers(self) -> list:
        """Containers do projeto compose de QA (vazio se não há nenhum)."""
        comando = ["docker", "compose", "-p", self.PROJETO_COMPOSE, "ps", "--all", "--format", "json"]
        resultado = self._docker(comando)
        texto = resultado.stdout.strip() if resultado else ""
        if not texto:
            return []
        if texto.startswith("["):
            return json.loads(texto)
        encontrados = []
        for linha in texto.splitlines():
            if linha.strip():
                encontrados.append(json.loads(linha))
        return encontrados

    def _portas_publicadas(self) -> set:
        """Portas do host já publicadas pelos containers da própria stack."""
        publicadas = set()
        for container in self.containers():
            for publicacao in container.get("Publishers") or []:
                porta = int(publicacao.get("PublishedPort") or 0)
                if porta:
                    publicadas.add(porta)
        return publicadas

    def _volume_existe(self) -> bool:
        """O volume do banco de QA já existe (a senha dele está gravada no volume)."""
        resultado = self._docker(["docker", "volume", "inspect", self.PROJETO_COMPOSE + "_banco_qa"])
        return bool(resultado) and resultado.returncode == 0

    def app_responde(self, porta_frontend: int) -> bool:
        """O frontend serve a SPA e o proxy chega ao backend (`/api/v1/products`)."""
        base = "http://127.0.0.1:" + str(porta_frontend)
        try:
            home = requests.get(base + "/", timeout=3)
            api = requests.get(base + "/api/v1/products", timeout=5)
        except requests.RequestException:
            return False
        return home.status_code == 200 and api.status_code == 200

    def _esperar_o_app(self, porta_frontend: int) -> bool:
        """Espera frontend + backend (o primeiro build e o boot levam um tempo)."""
        limite = time.monotonic() + self.ESPERA_EM_SEGUNDOS
        while time.monotonic() < limite:
            if self.app_responde(porta_frontend):
                return True
            time.sleep(3)
        return False

    # ── comandos ─────────────────────────────────────────────────────────

    def subir(self) -> int:
        """Confere as portas, garante credenciais, sobe a stack e espera o app."""
        config = self.ler_config()
        credenciais = self.credenciais.ler()
        if not credenciais:
            if self._volume_existe():
                print("credenciais locais ausentes e volume antigo presente — apagando os volumes de QA")
                self._docker(self._compose(["down", "-v"]), self._ambiente_do_compose(config, {}, self.portas_do_config(config)))
            credenciais = self.credenciais.gerar()
            print("credenciais locais geradas em " + self.credenciais.arquivo.name + " (fora do git)")

        antigas = self.portas_do_config(config)
        verificador = VerificadorDePortas(self._portas_publicadas())
        novas = {}
        novas["frontend"] = verificador.escolher(antigas["frontend"], self.FAIXA_FRONTEND, set())
        novas["backend"] = verificador.escolher(antigas["backend"], self.FAIXA_BACKEND, {novas["frontend"]})
        novas["banco"] = verificador.escolher(
            antigas["banco"], self.FAIXA_BANCO, {novas["frontend"], novas["backend"]}
        )
        if novas != antigas:
            self._reescrever_portas(antigas, novas)
            print("portas trocadas por estarem ocupadas: " + json.dumps(antigas) + " → " + json.dumps(novas)
                  + " (config.yaml atualizado)")
        else:
            print("portas livres confirmadas: " + json.dumps(novas))

        ambiente = self._ambiente_do_compose(config, credenciais, novas)
        print("==> docker compose up --build (projeto " + self.PROJETO_COMPOSE + ")")
        resultado = self._docker(self._compose(["up", "-d", "--build"]), ambiente)
        if resultado is None or resultado.returncode != 0:
            saida = (resultado.stdout + resultado.stderr) if resultado else ""
            print("docker compose up falhou:\n" + "\n".join(saida.strip().splitlines()[-25:]))
            return 1
        if not self._esperar_o_app(novas["frontend"]):
            print("o app não respondeu em " + str(self.ESPERA_EM_SEGUNDOS) + " s — veja: docker compose -p "
                  + self.PROJETO_COMPOSE + " logs backend")
            return 1
        print("stack de QA no ar: frontend http://127.0.0.1:" + str(novas["frontend"])
              + " · backend http://127.0.0.1:" + str(novas["backend"])
              + " · Postgres 127.0.0.1:" + str(novas["banco"]))
        return 0

    def descer(self, apagar_volumes: bool) -> int:
        """Para a stack; com `apagar_volumes`, apaga também banco e arquivos de QA."""
        config = self.ler_config()
        ambiente = self._ambiente_do_compose(config, self.credenciais.ler(), self.portas_do_config(config))
        argumentos = ["down", "-v"] if apagar_volumes else ["down"]
        resultado = self._docker(self._compose(argumentos), ambiente)
        if resultado is None or resultado.returncode != 0:
            print("docker compose down falhou")
            return 1
        print("stack de QA parada" + (" e volumes apagados" if apagar_volumes else ""))
        return 0

    def estado(self) -> int:
        """Mostra portas do config, containers da stack e se o app responde."""
        config = self.ler_config()
        portas = self.portas_do_config(config)
        print("config.yaml: " + json.dumps(portas))
        containers = self.containers()
        if not containers:
            print("nenhum container da stack de QA")
        for container in containers:
            print("  " + str(container.get("Service")) + ": " + str(container.get("State")) + " "
                  + str(container.get("Status", "")))
        print("app: " + ("responde" if self.app_responde(portas["frontend"]) else "não responde"))
        return 0


class LinhaDeComando:
    """Interpreta os argumentos e despacha para a StackDeQa."""

    def __call__(self) -> int:
        """Executa o comando pedido e devolve o código de saída."""
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("comando", choices=["subir", "descer", "zerar", "estado"])
        argumentos = parser.parse_args()
        stack = StackDeQa(PASTA)
        if argumentos.comando == "subir":
            return stack.subir()
        if argumentos.comando == "descer":
            return stack.descer(False)
        if argumentos.comando == "zerar":
            return stack.descer(True)
        return stack.estado()


if __name__ == "__main__":
    sys.exit(LinhaDeComando()())
