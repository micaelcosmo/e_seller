"""Credenciais da stack LOCAL de QA — geradas aleatoriamente, fora do git.

O arquivo `credenciais-locais.env` guarda a senha do Postgres de QA, os segredos
do backend de QA (JWT, chave do TOTP) e as senhas das contas de QA. Nada disso
vale em ambiente real: a stack é descartável (`stack.py zerar`).
Quem lê: `stack.py` (para subir o compose) e `adaptador.py` (para autenticar).
Nenhum valor daqui é impresso, gravado em evidência ou versionado.
"""

import base64
import secrets
from pathlib import Path


class CredenciaisLocais:
    """Lê e gera o `credenciais-locais.env` da stack de QA."""

    CHAVES_ALEATORIAS = [
        "QA_POSTGRES_PASSWORD",
        "QA_APP_SECRET_KEY",
        "QA_ADMIN_PASSWORD",
        "QA_CLIENTE_PASSWORD",
        "QA_SEM_COMPRAS_PASSWORD",
    ]
    CHAVES_FIXAS = {"QA_POSTGRES_USER": "eseller_qa", "QA_POSTGRES_DB": "eseller_qa"}

    def __init__(self, arquivo: Path) -> None:
        """Guarda o caminho do arquivo de credenciais (ele pode ainda não existir)."""
        self.arquivo = Path(arquivo)

    def existe(self) -> bool:
        """Verdadeiro quando a stack já subiu alguma vez nesta máquina."""
        return self.arquivo.exists()

    def ler(self) -> dict:
        """Valores do arquivo; vazio quando ele não existe."""
        valores: dict = {}
        if not self.arquivo.exists():
            return valores
        for linha in self.arquivo.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            valores[chave.strip()] = valor.strip()
        return valores

    def gerar(self) -> dict:
        """Gera valores aleatórios novos e grava o arquivo (sobrescreve)."""
        valores = dict(self.CHAVES_FIXAS)
        for chave in self.CHAVES_ALEATORIAS:
            valores[chave] = secrets.token_urlsafe(24)
        valores["QA_TOTP_ENCRYPTION_KEY"] = base64.b64encode(secrets.token_bytes(32)).decode()
        linhas = [
            "# Credenciais da stack LOCAL de QA do e_seller — geradas por stack.py.",
            "# Fora do git. Apagar este arquivo exige `stack.py zerar` (o banco guarda a senha).",
        ]
        for chave in valores:
            linhas.append(chave + "=" + valores[chave])
        self.arquivo.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        return valores

    def valor(self, chave: str) -> str:
        """Um valor do arquivo; erro claro quando a stack nunca subiu."""
        valores = self.ler()
        if chave not in valores:
            raise KeyError(
                "credencial '" + chave + "' ausente — suba a stack: python qa-harness/ambiente/stack.py subir"
            )
        return valores[chave]
