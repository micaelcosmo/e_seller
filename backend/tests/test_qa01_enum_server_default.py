"""Regressão: server_default de coluna enum compatível com o tipo do Postgres.

Spec: `.spec/unit/db/constraints.md` §5 e caso T5. O `Enum(<classe>)` cria o tipo
com os NOMES dos membros; um default com o valor (`'pending'`) derruba o
`create_all` num Postgres novo e o backend não sobe.
"""

from sqlalchemy import Enum

import app.main  # noqa: F401  (registra todos os models na metadata)
from app.core.db import Base


def test_server_default_de_enum_esta_entre_os_rotulos_do_tipo():
    """Toda coluna enum com server_default usa um rótulo existente no tipo."""
    incompativeis = []
    for tabela in Base.metadata.sorted_tables:
        for coluna in tabela.columns:
            if not isinstance(coluna.type, Enum) or coluna.server_default is None:
                continue
            padrao = str(coluna.server_default.arg).strip("'")
            if padrao not in coluna.type.enums:
                incompativeis.append(
                    tabela.name
                    + "."
                    + coluna.name
                    + " default="
                    + padrao
                    + " rótulos="
                    + ",".join(coluna.type.enums)
                )
    assert incompativeis == []
