"""CLI do harness — o que a skill `/qa` chama, igual em qualquer projeto.

    python qa-harness/executar.py <modo> [opções]

Modos que executam (bootstrap → massa → suítes → manifesto → relatório):
  completo        comentários em paralelo + integração + base visual (monitor)
                  + jornadas (monitor) + linhas do projeto + lint + catálogo + PDFs
  integracao      só as suítes de API do adaptador
  visual          base visual + jornadas, em monitor
  jornadas        só as jornadas  [dominio ...] [--jornada ID] [--viewport V]
  responsividade  base visual nos viewports de responsividade [--com-jornadas]
  linha NOME      uma linha declarada em linhas_do_projeto

Modos sobre execuções já feitas (sem bootstrap):
  consolidar [EXECUCAO]   aplica o revisao.yaml da IA e renderiza relatório (+PDF no completo)
  relatorios [EXECUCAO]   um PDF por história a partir do manifesto
  catalogo [EXECUCAO]     registra as imagens no CHANGELOG-EVIDENCIAS.yaml

Utilitários:
  comentarios [--execucao E] [--json] [--caminho P]   coletor para a IA julgar
  lint                  amarração história ↔ plano ↔ jornada ↔ evidência
  reverter [PASTA ...] [--conferir]   base64 → .png (ou só confere)
  olhar ROTA [PERFIL] [--viewport V]  print avulso para revisão
  bootstrap             só a verificação de ambiente

Saída: 0 tudo válido · 1 impedimento · 2 há falha de produto ou evidência inválida.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .adaptador import carregar_adaptador
from .configuracao import Configuracao
from .especificacao import Especificacao
from .evidencia import RegistradorDeEvidencias, ponto_de_dicionario
from .manifesto import Consolidador, Execucao, gravar_json, resolver_pasta_de_execucao

MODOS_QUE_EXECUTAM = ["completo", "integracao", "visual", "jornadas", "responsividade", "linha"]


class Harness:
    """Liga configuração, adaptador e especificação a cada modo."""

    def __init__(self, raiz_harness: Path) -> None:
        self._raiz_harness = Path(raiz_harness).resolve()
        self._config = Configuracao(self._raiz_harness)

    # ── modos que executam ───────────────────────────────────────────────

    def executar_modo(self, argumentos) -> int:
        modo = argumentos.modo
        if self._rodar_bootstrap() != 0:
            return 1
        adaptador = carregar_adaptador(self._config)
        especificacao = Especificacao(self._config)
        registrador = RegistradorDeEvidencias(self._config)
        viewports = self._viewports_do_modo(argumentos)
        execucao = Execucao(self._config, modo, viewports)
        execucao.preparar_pasta()
        print("==> execução " + execucao.carimbo + " (" + modo + ")")

        coletor = None
        if modo == "completo":
            coletor = self._disparar_coletor_de_comentarios(execucao)

        print("==> massa de dados")
        if not adaptador.preparar_massa():
            execucao.anotar_impedimento("massa de dados não foi aplicada — suítes não executadas")
            execucao.gravar()
            print("massa de dados falhou; nada executado")
            return 1

        if modo in ("completo", "integracao"):
            self._integracao(adaptador, registrador, execucao)
        if modo in ("completo", "visual", "responsividade"):
            self._base_visual(adaptador, especificacao, execucao, viewports)
        if modo in ("completo", "visual", "jornadas") or (modo == "responsividade" and argumentos.com_jornadas):
            for viewport in viewports:
                self._jornadas(adaptador, especificacao, execucao, viewport, argumentos)
        if modo == "completo":
            for nome in self._config.linhas_do_projeto:
                if self._config.linhas_do_projeto[nome].get("no_completo"):
                    self._linha_do_projeto(nome, execucao)
        if modo == "linha":
            self._linha_do_projeto(argumentos.nome, execucao)

        print("==> lint da cadeia de teste")
        achados = self._lint(especificacao, execucao.pontos)
        execucao.anotar_lint(achados)
        print("    " + str(len(achados)) + " lacuna(s) de especificação")

        if coletor is not None:
            execucao.anotar_comentarios(self._aguardar_coletor(coletor, execucao))

        execucao.gravar()
        if self._produziu_imagens(execucao.pontos):
            self._catalogar(execucao.pasta)
        if modo == "completo":
            self._gerar_pdfs(execucao.pasta)
        return self._placar(execucao)

    def _viewports_do_modo(self, argumentos) -> list:
        if argumentos.modo == "responsividade":
            return self._config.viewports_de_responsividade
        viewport = getattr(argumentos, "viewport", None)
        if viewport:
            return [viewport]
        return ["monitor"]

    def _rodar_bootstrap(self) -> int:
        print("==> bootstrap")
        from .bootstrap import Bootstrap

        return Bootstrap(self._raiz_harness).executar()

    def _integracao(self, adaptador, registrador, execucao) -> None:
        print("==> suítes de integração")
        for classe in adaptador.suites_de_integracao():
            suite = classe(self._config, adaptador, registrador)
            try:
                pontos = suite.executar()
            except Exception as erro:
                execucao.anotar_impedimento(
                    "suíte " + str(getattr(classe, "dominio", classe.__name__)) + " quebrou: "
                    + type(erro).__name__ + ": " + str(erro)[:200]
                )
                print("    - " + str(getattr(classe, "dominio", "?")) + ": QUEBROU (" + type(erro).__name__ + ")")
                continue
            execucao.adicionar(pontos)
            validos = 0
            for ponto in pontos:
                if ponto.veredito == "VALIDO":
                    validos = validos + 1
            print("    - " + suite.dominio + ": " + str(validos) + "/" + str(len(pontos)) + " válidos")

    def _base_visual(self, adaptador, especificacao, execucao, viewports) -> None:
        print("==> base visual (" + ", ".join(viewports) + ")")
        from .base_visual import BaseVisual

        execucao.adicionar(BaseVisual(self._config, adaptador, especificacao, viewports).executar())

    def _jornadas(self, adaptador, especificacao, execucao, viewport, argumentos) -> None:
        print("==> jornadas (" + viewport + ")")
        from .jornadas import RunnerDeJornadas

        dominios = getattr(argumentos, "dominios", None) or []
        so_jornada = getattr(argumentos, "jornada", "") or ""
        runner = RunnerDeJornadas(self._config, adaptador, especificacao, viewport, dominios, so_jornada)
        execucao.adicionar(runner.executar())

    def _linha_do_projeto(self, nome: str, execucao) -> None:
        declaracao = self._config.linhas_do_projeto.get(nome)
        if not declaracao:
            execucao.anotar_impedimento("linha '" + nome + "' não declarada em linhas_do_projeto")
            return
        print("==> linha do projeto: " + nome)
        comando = list(declaracao.get("comando") or [])
        if comando and comando[0] in ("python", "python3", "py"):
            comando[0] = sys.executable
        resultado = subprocess.run(comando, cwd=str(self._config.raiz_projeto))
        pontos = []
        caminho = self._config.raiz_projeto / str(declaracao.get("resultado", ""))
        if declaracao.get("resultado") and caminho.is_file():
            dados = json.loads(caminho.read_text(encoding="utf-8"))
            if isinstance(dados, dict):
                dados = dados.get("pontos") or []
            for registro in dados:
                pontos.append(ponto_de_dicionario(registro))
        execucao.adicionar(pontos)
        execucao.anotar_linha(nome, {
            "codigo_de_saida": resultado.returncode,
            "pontos": len(pontos),
            "observacao": "impedimento (saída 1)" if resultado.returncode == 1 else "",
        })

    def _lint(self, especificacao, pontos) -> list:
        from .lint_historias import LintDaCadeia

        return LintDaCadeia(self._config, especificacao).executar(pontos)

    def _disparar_coletor_de_comentarios(self, execucao):
        """O coletor não usa banco nem navegador: roda em paralelo com as suítes."""
        destino = execucao.pasta / "comentarios.json"
        comando = [
            sys.executable,
            str(self._raiz_harness / "executar.py"),
            "comentarios",
            "--execucao",
            execucao.carimbo,
        ]
        print("==> comentários: coletor disparado em paralelo → " + self._config.relativo(destino))
        return subprocess.Popen(comando, cwd=str(self._config.raiz_projeto), stdout=subprocess.DEVNULL)

    def _aguardar_coletor(self, processo, execucao) -> dict:
        processo.wait()
        caminho = execucao.pasta / "comentarios.json"
        if not caminho.exists():
            return {"arquivo": "", "total": 0, "erro": "coletor não gravou comentarios.json"}
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        return {
            "arquivo": self._config.relativo(caminho),
            "regra": dados.get("regra"),
            "total": dados.get("total", 0),
            "por_categoria": dados.get("por_categoria", {}),
        }

    def _produziu_imagens(self, pontos) -> bool:
        for ponto in pontos:
            for caminho in ponto.evidencias:
                if str(caminho).endswith(".png"):
                    return True
        return False

    def _placar(self, execucao) -> int:
        contagem: dict = {}
        for ponto in execucao.pontos:
            contagem[ponto.veredito] = contagem.get(ponto.veredito, 0) + 1
        partes = []
        for veredito in ("VALIDO", "FALHA DE PRODUTO", "EVIDENCIA INVALIDA", "INCONCLUSIVO"):
            partes.append(veredito + "=" + str(contagem.get(veredito, 0)))
        print("")
        print("placar automático: " + " · ".join(partes))
        print("relatório: " + self._config.relativo(execucao.pasta / "relatorio.md"))
        print("próximo passo: revisão de validade → " + self._config.relativo(execucao.pasta / "revisao.yaml")
              + " → python qa-harness/executar.py consolidar " + execucao.carimbo)
        if contagem.get("FALHA DE PRODUTO") or contagem.get("EVIDENCIA INVALIDA"):
            return 2
        return 0

    # ── modos sobre execuções feitas ─────────────────────────────────────

    def consolidar(self, argumentos) -> int:
        pasta = resolver_pasta_de_execucao(self._config, argumentos.execucao or "")
        if pasta is None:
            print("nenhuma execução encontrada — rode um modo que executa antes")
            return 1
        manifesto = Consolidador(self._config, pasta).executar()
        print("consolidado: " + self._config.relativo(pasta / "relatorio.md"))
        revisao = manifesto.get("revisao") or {}
        print("  vereditos alterados pela revisão: " + str(revisao.get("vereditos_alterados", 0)))
        for nome in revisao.get("pontos_nao_encontrados") or []:
            print("  aviso: ponto do revisao.yaml não encontrado: " + nome)
        if argumentos.sem_pdf:
            return 0
        if manifesto.get("modo") == "completo" or argumentos.pdf:
            self._gerar_pdfs(pasta)
        return 0

    def relatorios(self, argumentos) -> int:
        pasta = resolver_pasta_de_execucao(self._config, argumentos.execucao or "")
        if pasta is None:
            print("nenhum manifesto encontrado — é preciso executar uma suíte antes (ex.: /qa completo)")
            return 1
        return self._gerar_pdfs(pasta)

    def catalogo(self, argumentos) -> int:
        pasta = resolver_pasta_de_execucao(self._config, argumentos.execucao or "")
        if pasta is None:
            print("nenhum manifesto encontrado")
            return 1
        return self._catalogar(pasta)

    def _gerar_pdfs(self, pasta: Path) -> int:
        print("==> PDFs por história")
        from .relatorio_pdf import RelatorioEmPdf

        return RelatorioEmPdf(self._config, pasta).executar()

    def _catalogar(self, pasta: Path) -> int:
        print("==> catálogo de evidências")
        from .catalogo import ChangelogDeEvidencias

        return ChangelogDeEvidencias(self._config, pasta).executar()

    # ── utilitários ──────────────────────────────────────────────────────

    def comentarios(self, argumentos) -> int:
        from .lint_comentarios import ColetorDeComentarios, resumir

        candidatos = ColetorDeComentarios(self._config, argumentos.caminho).executar()
        regra = self._config.relativo(self._config.caminho("convencao_de_comentarios"))
        if argumentos.execucao:
            destino = self._config.caminho("relatorios") / argumentos.execucao / "comentarios.json"
            gravar_json(destino, {
                "regra": regra,
                "natureza": "candidatos a warning — quem julga é a IA na etapa /qa comentarios",
                "total": len(candidatos),
                "por_categoria": resumir(candidatos),
                "candidatos": candidatos,
            })
        if argumentos.json:
            print(json.dumps(candidatos, ensure_ascii=False, indent=2))
            return 0
        print("comentários: " + str(len(candidatos)) + " candidato(s) para a IA julgar (regra: " + regra + ")")
        resumo = resumir(candidatos)
        for categoria in sorted(resumo):
            print("  " + categoria + ": " + str(resumo[categoria]))
        return 0

    def lint(self, argumentos) -> int:
        achados = self._lint(Especificacao(self._config), None)
        if not achados:
            print("lint: OK — cadeia história ↔ plano ↔ jornada ↔ evidência amarrada")
            return 0
        print("lint: " + str(len(achados)) + " lacuna(s)")
        for achado in achados:
            print("  - " + achado)
        return 2

    def reverter(self, argumentos) -> int:
        from .reverter import Reversao

        alvos = []
        for bruto in argumentos.caminhos or []:
            alvos.append(Path(bruto).resolve())
        if not alvos:
            alvos = [self._config.caminho("evidencias")]
        return Reversao(self._config, alvos, argumentos.conferir).executar()

    def olhar(self, argumentos) -> int:
        from .olhar import OlharTela

        adaptador = carregar_adaptador(self._config)
        return OlharTela(self._config, adaptador).executar(argumentos.rota, argumentos.perfil, argumentos.viewport)

    def bootstrap(self, argumentos) -> int:
        return self._rodar_bootstrap()


def montar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="executar.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    modos = parser.add_subparsers(dest="modo", required=True)

    modos.add_parser("completo")
    modos.add_parser("integracao")
    visual = modos.add_parser("visual")
    visual.add_argument("--viewport")
    jornadas = modos.add_parser("jornadas")
    jornadas.add_argument("dominios", nargs="*")
    jornadas.add_argument("--jornada")
    jornadas.add_argument("--viewport")
    responsividade = modos.add_parser("responsividade")
    responsividade.add_argument("--com-jornadas", action="store_true", dest="com_jornadas")
    linha = modos.add_parser("linha")
    linha.add_argument("nome")

    for nome in ("relatorios", "catalogo"):
        sub = modos.add_parser(nome)
        sub.add_argument("execucao", nargs="?")
    consolidar = modos.add_parser("consolidar")
    consolidar.add_argument("execucao", nargs="?")
    consolidar.add_argument("--pdf", action="store_true")
    consolidar.add_argument(
        "--sem-pdf", action="store_true", dest="sem_pdf",
        help="execução já superada: as imagens em disco são de outra execução",
    )

    comentarios = modos.add_parser("comentarios")
    comentarios.add_argument("--execucao")
    comentarios.add_argument("--json", action="store_true")
    comentarios.add_argument("--caminho", action="append")
    modos.add_parser("lint")
    reverter = modos.add_parser("reverter")
    reverter.add_argument("caminhos", nargs="*")
    reverter.add_argument("--conferir", action="store_true")
    olhar = modos.add_parser("olhar")
    olhar.add_argument("rota")
    olhar.add_argument("perfil", nargs="?", default="visitante")
    olhar.add_argument("--viewport", default="monitor")
    modos.add_parser("bootstrap")
    return parser


def principal(raiz_harness: Path, argv: list) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    argumentos = montar_parser().parse_args(argv)
    harness = Harness(raiz_harness)
    if argumentos.modo in MODOS_QUE_EXECUTAM:
        return harness.executar_modo(argumentos)
    metodo = getattr(harness, argumentos.modo)
    return metodo(argumentos)
