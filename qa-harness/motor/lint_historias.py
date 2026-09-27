"""Lint da cadeia de teste — história, plano, jornada e evidência amarrados.

História de usuário que toca o frontend tem prova visual percorrendo o caminho,
com começo e fim marcados. Um domínio é "com tela" quando o arquivo de
histórias declara `**Jornadas:** <caminho>` no cabeçalho; nele, toda história
precisa de ao menos uma jornada, salvo `**Prova visual:** não se aplica — <motivo>`.

Devolve achados (lacunas de especificação) — não altera nada.
"""

import re

from .especificacao import normalizar
from .evidencia_de_pasta import LeitorDeEvidencia
from .jornadas import ACOES_DE_VERIFICACAO

PADRAO_PONTO = re.compile(r"^Ponto \d+ - \S")


class LintDaCadeia:
    """Confere a amarração estática e, quando já executadas, as evidências."""

    def __init__(self, config, especificacao) -> None:
        self._config = config
        self._spec = especificacao
        self._achados: list = []

    def executar(self, pontos_executados: list = None) -> list:
        jornadas = self._spec.jornadas()
        self._conferir_carimbo_das_historias()
        self._conferir_jornadas(jornadas)
        self._conferir_cobertura_visual(jornadas)
        self._conferir_planos()
        self._conferir_marcos(jornadas)
        if pontos_executados is not None:
            self._conferir_plano_contra_execucao(pontos_executados)
        return self._achados

    def _achado(self, texto: str) -> None:
        self._achados.append(texto)

    def _conferir_carimbo_das_historias(self) -> None:
        arquivos = self._spec.arquivos_de_historias()
        for dominio in arquivos:
            cabecalho = arquivos[dominio].texto.split("\n## ", 1)[0]
            if "**Derivado de:**" not in cabecalho:
                self._achado("histórias de '" + dominio + "' sem carimbo **Derivado de:** no cabeçalho")

    def _conferir_jornadas(self, jornadas: list) -> None:
        perfis = self._config.perfis
        vistos: dict = {}
        for jornada in jornadas:
            identificador = str(jornada.get("id", "?"))
            dominio = str(jornada.get("_dominio"))
            chave = (dominio, identificador)
            if chave in vistos:
                self._achado("jornada '" + identificador + "' repetida em " + dominio)
            vistos[chave] = True
            historia = jornada.get("historia")
            if not historia:
                self._achado("jornada '" + identificador + "' não declara história de usuário")
            elif self._spec.historia(historia) is None:
                self._achado("jornada '" + identificador + "' cita história inexistente: " + str(historia))
            entrada = str(jornada.get("entra_como") or "visitante")
            if entrada != "visitante" and entrada not in perfis:
                self._achado("jornada '" + identificador + "' entra como perfil inexistente: " + entrada)
            passos = jornada.get("passos") or []
            if len(passos) < 2:
                self._achado("jornada '" + identificador + "' tem menos de dois passos — sem início e fim não há caminho")
            verifica = False
            for passo in passos:
                acao = passo.get("acao")
                if acao in ACOES_DE_VERIFICACAO:
                    verifica = True
                if acao == "entrar_como":
                    perfil = str(passo.get("perfil"))
                    if perfil != "visitante" and perfil not in perfis:
                        self._achado("jornada '" + identificador + "' troca para perfil inexistente: " + perfil)
                if not passo.get("titulo"):
                    self._achado("jornada '" + identificador + "' tem passo sem título (vira legenda do print)")
            if not verifica:
                self._achado(
                    "jornada '" + identificador + "' só navega: sem passo de conferência ela não prova a funcionalidade"
                )

    def _conferir_cobertura_visual(self, jornadas: list) -> None:
        citadas = set()
        for jornada in jornadas:
            if jornada.get("historia"):
                citadas.add(normalizar(jornada["historia"]))
        arquivos = self._spec.arquivos_de_historias()
        for historia in self._spec.historias():
            arquivo = arquivos.get(historia.dominio)
            if arquivo is None or not arquivo.tem_tela:
                continue
            if historia.prova_visual_dispensada:
                continue
            if normalizar(historia.nome) not in citadas:
                self._achado(
                    historia.dominio + ": '" + historia.nome + "' toca o frontend e não tem jornada (prova visual obrigatória)"
                )

    def _conferir_planos(self) -> None:
        for ponto in self._spec.pontos_de_plano():
            origem = self._config.relativo(ponto.arquivo)
            if not PADRAO_PONTO.match(ponto.nome):
                self._achado(origem + ": nome fora da convenção 'Ponto <n> - <título>': " + ponto.nome)
            if not ponto.validade:
                self._achado(origem + ": '" + ponto.nome + "' sem campo validade")
            if not ponto.historia:
                self._achado(origem + ": '" + ponto.nome + "' não referencia história")
            elif self._spec.historia(ponto.historia) is None:
                self._achado(origem + ": '" + ponto.nome + "' cita história inexistente: " + ponto.historia)

    def _conferir_marcos(self, jornadas: list) -> None:
        """Jornada executada por inteiro precisa ter INICIO e FIM na evidência."""
        raiz = self._config.caminho("evidencias") / "jornadas"
        if not raiz.exists():
            return
        declaradas = set()
        for jornada in jornadas:
            declaradas.add((str(jornada.get("_dominio")), str(jornada.get("id"))))
        for arquivo in sorted(raiz.rglob("evidencias.json")):
            leitor = LeitorDeEvidencia(arquivo.parent)
            conteudo = leitor.conteudo()
            chave = (str(conteudo.get("dominio")), str(conteudo.get("jornada")))
            if chave not in declaradas:
                self._achado(self._config.relativo(arquivo.parent) + ": evidência de jornada que não está mais declarada")
                continue
            if conteudo.get("passos_executados") != conteudo.get("passos_declarados"):
                continue
            marcos = set()
            for dados in leitor.imagens().values():
                marcos.add(dados.get("marco"))
            if "INICIO" not in marcos or "FIM" not in marcos:
                self._achado("jornada '" + chave[1] + "' não gravou INICIO e FIM nas evidências")

    def _conferir_plano_contra_execucao(self, pontos: list) -> None:
        """Ponto de integração do plano sem teste, ou teste sem ponto no plano."""
        executados = set()
        dominios_executados = set()
        for ponto in pontos:
            if ponto.suite != "integracao":
                continue
            executados.add((ponto.dominio, normalizar(ponto.nome)))
            dominios_executados.add(ponto.dominio)
            if self._spec.ponto(ponto.nome, ponto.dominio) is None:
                self._achado(ponto.dominio + ": '" + ponto.nome + "' executado sem ponto correspondente no plano")
        for ponto in self._spec.pontos_de_plano():
            if ponto.suite != "integracao" or ponto.dominio not in dominios_executados:
                continue
            if (ponto.dominio, normalizar(ponto.nome)) not in executados:
                self._achado(ponto.dominio + ": '" + ponto.nome + "' está no plano e não tem teste")
