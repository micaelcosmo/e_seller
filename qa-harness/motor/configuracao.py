"""Leitura do `qa-harness/config.yaml` do projeto e do `.env` da raiz.

Nenhuma URL, conta, caminho ou limite é escrito no motor: tudo o que muda de um
projeto para outro passa por aqui. Chave ausente no YAML cai no padrão abaixo.
"""

from pathlib import Path

import yaml

CAMINHOS_PADRAO = {
    "historias": "spec/test/historias",
    "planos": "spec/test/planos",
    "jornadas": "spec/test/jornadas",
    "base_visual": "spec/test/planos/_base-visual.yaml",
    "evidencias": "qa-harness/evidencias",
    "relatorios": "qa-harness/relatorios",
    "convencao_de_comentarios": "spec/code/convencao-de-comentarios.md",
}

EXECUCAO_PADRAO = {
    "healing_maximo": 3,
    "headless": True,
    "timeout_ms": 30000,
    "texto_minimo_renderizado": 200,
    "tentativas_de_assentamento": 20,
    "intervalo_de_assentamento_ms": 1500,
}

VIEWPORTS_PADRAO = {
    "monitor": {"largura": 1920, "altura": 1080},
    "notebook": {"largura": 1366, "altura": 768},
    "celular": {"largura": 390, "altura": 844, "device": True},
}

COMENTARIOS_PADRAO = {
    "alvos": ["src", "qa-harness"],
    "extensoes": [".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".css"],
    "ignorar": [
        "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next",
        "evidencias", "relatorios", "motor",
    ],
}


class Configuracao:
    """Configuração viva do harness de um projeto."""

    def __init__(self, raiz_harness: Path) -> None:
        self._raiz_harness = Path(raiz_harness).resolve()
        self._raiz_projeto = self._raiz_harness.parent
        self._dados = self._carregar_yaml()
        self._env = self._carregar_env()

    def _carregar_yaml(self) -> dict:
        """Lê o config.yaml; sem ele o harness não sabe onde bater."""
        caminho = self._raiz_harness / "config.yaml"
        if not caminho.exists():
            raise FileNotFoundError(
                "qa-harness/config.yaml não encontrado — ver adotar.md da skill /qa"
            )
        with open(caminho, encoding="utf-8") as arquivo:
            dados = yaml.safe_load(arquivo) or {}
        return dados

    def _carregar_env(self) -> dict:
        """Lê o `.env` da raiz do projeto, quando existe."""
        variaveis: dict = {}
        caminho = self._raiz_projeto / ".env"
        if not caminho.exists():
            return variaveis
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            variaveis[chave.strip()] = valor.strip().strip('"').strip("'")
        return variaveis

    # ── identidade ───────────────────────────────────────────────────────

    @property
    def raiz_projeto(self) -> Path:
        """Raiz do repositório testado."""
        return self._raiz_projeto

    @property
    def raiz_harness(self) -> Path:
        """Pasta `qa-harness/` do projeto."""
        return self._raiz_harness

    @property
    def dados(self) -> dict:
        """O YAML inteiro, para chaves que só o adaptador do projeto entende."""
        return self._dados

    @property
    def env(self) -> dict:
        """Variáveis do `.env` da raiz."""
        return self._env

    def _projeto(self) -> dict:
        return self._dados.get("projeto") or {}

    @property
    def nome_do_projeto(self) -> str:
        """Nome do projeto, usado no relatório e no PDF."""
        return str(self._projeto().get("nome") or self._raiz_projeto.name)

    @property
    def assinatura_da_aplicacao(self) -> str:
        """Texto que só esta aplicação tem na home (confere a porta certa)."""
        return str(self._projeto().get("assinatura_da_aplicacao") or "")

    @property
    def produto_somente_leitura(self) -> list:
        """Pastas do produto que o QA lê e nunca edita."""
        return list(self._projeto().get("produto_somente_leitura") or [])

    @property
    def arquivo_de_status(self) -> str:
        """Arquivo de status com seção de QA a atualizar, quando o projeto tem."""
        return str(self._projeto().get("arquivo_de_status") or "")

    # ── URLs ─────────────────────────────────────────────────────────────

    def _urls(self) -> dict:
        return self._dados.get("urls") or {}

    @property
    def url_app(self) -> str:
        """Onde o navegador abre as telas."""
        return str(self._urls().get("app", "")).rstrip("/")

    @property
    def url_api(self) -> str:
        """Base das chamadas de integração; cai na URL do app quando é um monolito."""
        api = self._urls().get("api") or self._urls().get("app", "")
        return str(api).rstrip("/")

    @property
    def healthcheck(self) -> str:
        """Caminho que o bootstrap consulta para saber se a aplicação está de pé."""
        return str(self._urls().get("healthcheck", "/"))

    # ── perfis e viewports ───────────────────────────────────────────────

    @property
    def perfis(self) -> dict:
        """Perfis declarados; `visitante` é sempre o perfil sem sessão."""
        return self._dados.get("perfis") or {}

    def perfil(self, nome: str) -> dict:
        """Dados de um perfil, com mensagem útil quando ele não existe."""
        if nome not in self.perfis:
            disponiveis = ", ".join(self.perfis.keys())
            raise KeyError(f"perfil '{nome}' não existe — disponíveis: {disponiveis}")
        return self.perfis[nome] or {}

    def perfil_tem_conta(self, nome: str) -> bool:
        """Visitante e perfil sem `conta` navegam sem sessão."""
        if nome == "visitante":
            return False
        return bool(self.perfil(nome).get("conta"))

    def perfis_com_conta(self) -> list:
        """Perfis que precisam autenticar."""
        encontrados = []
        for nome in self.perfis:
            if self.perfil_tem_conta(nome):
                encontrados.append(nome)
        return encontrados

    @property
    def viewports(self) -> dict:
        """Matriz de viewports; monitor é o padrão de toda evidência."""
        return self._dados.get("viewports") or VIEWPORTS_PADRAO

    def viewport(self, nome: str) -> dict:
        """Dimensões de um viewport declarado."""
        if nome not in self.viewports:
            raise KeyError(f"viewport '{nome}' não declarado no config.yaml")
        return self.viewports[nome]

    @property
    def viewports_de_responsividade(self) -> list:
        """Viewports do modo responsividade (padrão: tudo menos monitor)."""
        declarados = self._dados.get("responsividade")
        if declarados:
            return list(declarados)
        outros = []
        for nome in self.viewports:
            if nome != "monitor":
                outros.append(nome)
        return outros

    # ── execução ─────────────────────────────────────────────────────────

    def _execucao(self, chave: str):
        dados = self._dados.get("execucao") or {}
        if chave in dados:
            return dados[chave]
        return EXECUCAO_PADRAO[chave]

    @property
    def headless(self) -> bool:
        return bool(self._execucao("headless"))

    @property
    def timeout_ms(self) -> int:
        return int(self._execucao("timeout_ms"))

    @property
    def timeout_de_navegacao_ms(self) -> int:
        """Limite de uma navegação; servidor de desenvolvimento compila rota no primeiro acesso."""
        dados = self._dados.get("execucao") or {}
        if "timeout_de_navegacao_ms" in dados:
            return int(dados["timeout_de_navegacao_ms"])
        return self.timeout_ms * 3

    @property
    def altura_maxima_da_captura_px(self) -> int:
        """Teto da captura de página inteira (padrão: 4 alturas do monitor)."""
        dados = self._dados.get("execucao") or {}
        if "altura_maxima_da_captura_px" in dados:
            return int(dados["altura_maxima_da_captura_px"])
        return 4320

    @property
    def healing_maximo(self) -> int:
        return int(self._execucao("healing_maximo"))

    @property
    def texto_minimo_renderizado(self) -> int:
        """Abaixo disso a tela está em branco, em erro ou presa carregando."""
        return int(self._execucao("texto_minimo_renderizado"))

    @property
    def tentativas_de_assentamento(self) -> int:
        return int(self._execucao("tentativas_de_assentamento"))

    @property
    def intervalo_de_assentamento_ms(self) -> int:
        return int(self._execucao("intervalo_de_assentamento_ms"))

    # ── caminhos ─────────────────────────────────────────────────────────

    def caminho(self, chave: str) -> Path:
        """Caminho absoluto de uma pasta ou arquivo da cadeia de QA."""
        declarados = self._dados.get("caminhos") or {}
        relativo = declarados.get(chave) or CAMINHOS_PADRAO[chave]
        return self._raiz_projeto / relativo

    def relativo(self, caminho: Path) -> str:
        """Caminho relativo à raiz do projeto, sempre com barra normal."""
        absoluto = Path(caminho).resolve()
        return absoluto.relative_to(self._raiz_projeto.resolve()).as_posix()

    # ── etapas opcionais ─────────────────────────────────────────────────

    @property
    def comentarios(self) -> dict:
        """Alvos, extensões e pastas ignoradas pelo coletor de comentários."""
        declarados = self._dados.get("comentarios") or {}
        combinado = dict(COMENTARIOS_PADRAO)
        combinado.update(declarados)
        return combinado

    @property
    def linhas_do_projeto(self) -> dict:
        """Linhas extras (unitários, fluxogramas...) que só este projeto tem."""
        return self._dados.get("linhas_do_projeto") or {}

    @property
    def dependencias_extras(self) -> list:
        """Módulos Python que o adaptador do projeto importa além dos do motor."""
        return list(self._dados.get("dependencias_extras") or [])
