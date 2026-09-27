"""Porta de entrada do harness de QA — delega tudo ao motor agnóstico.

Uso: python qa-harness/executar.py <modo> [opções]   (ver --help)
O motor (qa-harness/motor/) é instalado pela skill /qa; não se edita aqui.
"""

import sys
from pathlib import Path

RAIZ_HARNESS = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ_HARNESS))

from motor.executar import principal  # noqa: E402

if __name__ == "__main__":
    sys.exit(principal(RAIZ_HARNESS, sys.argv[1:]))
