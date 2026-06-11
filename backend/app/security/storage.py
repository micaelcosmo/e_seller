"""Armazenamento protegido de arquivos de e-book (anti path traversal)."""

from pathlib import Path


class PathTraversalError(Exception):
    """Levantada quando um caminho tenta escapar do diretório protegido."""


class FileMissing(Exception):
    """Levantada quando o arquivo solicitado não existe no armazenamento."""


class ProtectedStorage:
    """Resolve e lê arquivos garantindo que fiquem dentro da raiz protegida."""

    def __init__(self, root: str | Path) -> None:
        """Define a raiz protegida (criando o diretório se necessário)."""
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, relative_name: str) -> Path:
        """Resolve o caminho dentro da raiz; bloqueia path traversal."""
        candidate = (self.root / relative_name).resolve()
        if self.root not in candidate.parents and candidate != self.root:
            raise PathTraversalError(relative_name)
        return candidate

    def read_bytes(self, relative_name: str) -> bytes:
        """Lê e retorna os bytes do arquivo; levanta FileMissing se ausente."""
        path = self.resolve(relative_name)
        if not path.is_file():
            raise FileMissing(relative_name)
        return path.read_bytes()

    def write_bytes(self, relative_name: str, data: bytes) -> None:
        """Escreve bytes em um arquivo dentro da raiz protegida."""
        path = self.resolve(relative_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
