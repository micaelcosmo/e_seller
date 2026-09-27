"""Bootstrap — nenhuma suíte roda com ambiente quebrado.

Evidência colhida de ambiente quebrado é pior que evidência nenhuma, porque
parece prova. Ordem:
1. dependências Python do motor e as extras do projeto;
2. `config.yaml` carregável e adaptador carregável;
3. Chromium do Playwright — baixa/atualiza sozinho se faltar;
4. aplicação respondendo **e sendo esta aplicação** (assinatura na home);
5. verificações do projeto (`Adaptador.verificar_ambiente`: banco, schema, contas);
6. motor do projeto na mesma versão do motor global (aviso, não bloqueia).
"""

import importlib
import subprocess
import sys
from pathlib import Path

DEPENDENCIAS_DO_MOTOR = ["requests", "yaml", "playwright", "fpdf", "PIL"]


class Bootstrap:
    """Verificador de ambiente; devolve 0 (pronto) ou 1 (impedimentos)."""

    def __init__(self, raiz_harness: Path) -> None:
        self._raiz_harness = Path(raiz_harness)
        self._falhas: list = []
        self._avisos: list = []
        self._config = None
        self._adaptador = None

    def executar(self) -> int:
        self._verificar_dependencias(DEPENDENCIAS_DO_MOTOR)
        if self._falhas:
            return self._relatorio()
        self._carregar_config()
        if self._falhas:
            return self._relatorio()
        self._verificar_dependencias(self._config.dependencias_extras)
        self._carregar_adaptador()
        if self._falhas:
            return self._relatorio()
        self._provisionar_navegador()
        self._verificar_aplicacao()
        if not self._falhas:
            self._verificar_projeto()
        self._comparar_versao_do_motor()
        return self._relatorio()

    def _verificar_dependencias(self, modulos: list) -> None:
        for modulo in modulos:
            try:
                importlib.import_module(modulo)
            except ImportError:
                self._falhas.append(
                    "dependência ausente: " + modulo + " (rode: pip install -r qa-harness/requirements.txt)"
                )

    def _carregar_config(self) -> None:
        try:
            from .configuracao import Configuracao

            self._config = Configuracao(self._raiz_harness)
        except Exception as erro:
            self._falhas.append("config.yaml não carregou: " + str(erro))

    def _carregar_adaptador(self) -> None:
        try:
            from .adaptador import carregar_adaptador

            self._adaptador = carregar_adaptador(self._config)
        except Exception as erro:
            self._falhas.append("qa-harness/adaptador.py não carregou: " + type(erro).__name__ + ": " + str(erro)[:200])

    def _provisionar_navegador(self) -> None:
        """`playwright install chromium` é idempotente: baixa, atualiza ou não faz nada."""
        comando = [sys.executable, "-m", "playwright", "install", "chromium"]
        try:
            resultado = subprocess.run(comando, capture_output=True, text=True, timeout=900)
        except (FileNotFoundError, subprocess.TimeoutExpired) as erro:
            self._falhas.append("não consegui provisionar o Chromium: " + type(erro).__name__)
            return
        if resultado.returncode != 0:
            self._falhas.append("playwright install chromium falhou: " + resultado.stderr.strip()[:200])

    def _verificar_aplicacao(self) -> None:
        import requests

        url = self._config.url_app + self._config.healthcheck
        try:
            resposta = requests.get(url, timeout=90)
        except requests.RequestException:
            self._falhas.append("aplicação fora do ar em " + url)
            return
        if resposta.status_code >= 500:
            self._falhas.append("aplicação respondeu " + str(resposta.status_code) + " em " + url)
            return
        assinatura = self._config.assinatura_da_aplicacao
        if assinatura and assinatura not in resposta.text:
            self._falhas.append(
                "a porta de " + url + " responde, mas não parece ser " + self._config.nome_do_projeto
                + " (não achei '" + assinatura + "' na resposta) — outro projeto pode estar na porta"
            )

    def _verificar_projeto(self) -> None:
        try:
            impedimentos = self._adaptador.verificar_ambiente()
        except Exception as erro:
            impedimentos = ["verificação do projeto quebrou: " + type(erro).__name__ + ": " + str(erro)[:200]]
        for impedimento in impedimentos or []:
            self._falhas.append(impedimento)

    def _comparar_versao_do_motor(self) -> None:
        local = Path(__file__).resolve().parent / "VERSAO"
        global_ = Path.home() / ".claude" / "skills" / "qa" / "motor" / "VERSAO"
        if not local.exists() or not global_.exists():
            return
        versao_local = local.read_text(encoding="utf-8").strip()
        versao_global = global_.read_text(encoding="utf-8").strip()
        if versao_local != versao_global:
            self._avisos.append(
                "motor do projeto " + versao_local + " ≠ motor global " + versao_global
                + " — rode: python ~/.claude/skills/qa/sincronizar.py ."
            )

    def _relatorio(self) -> int:
        for aviso in self._avisos:
            print("aviso: " + aviso)
        if not self._falhas:
            print("bootstrap OK — ambiente pronto para as suítes")
            return 0
        print("bootstrap FALHOU — impedimentos:")
        for falha in self._falhas:
            print("  - " + falha)
        return 1
