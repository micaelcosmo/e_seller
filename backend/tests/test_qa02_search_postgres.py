"""Regressão QAF-02: a busca do catálogo precisa compilar SQL válido para o Postgres.

Spec: `.spec/enrichment/roadmap-qaf.md` (QAF-02). No Postgres, `SELECT DISTINCT`
exige que toda expressão do `ORDER BY` esteja no select — a relevância da busca
(`CASE ...`) não está, e a busca respondia 500. Os testes rodam em SQLite, que
aceita; por isso o teste compila o statement para o dialeto do Postgres.
"""

from sqlalchemy.dialects import postgresql

from app.catalog.repository import ProductRepository


class _SessaoQueNaoExecuta:
    """Sessão falsa: o teste só compila o statement, não vai ao banco."""


def _sql_postgres(**filtros) -> str:
    """SQL da listagem compilado para o Postgres, com os filtros pedidos."""
    repositorio = ProductRepository(_SessaoQueNaoExecuta())
    statement = repositorio.build_list_statement(**filtros)
    return str(statement.compile(dialect=postgresql.dialect())).upper()


def test_busca_com_relevancia_nao_usa_distinct():
    """Com `q`, a ordenação por relevância convive com o SQL do Postgres."""
    sql = _sql_postgres(query="fastapi")
    assert "ORDER BY CASE" in sql
    assert "DISTINCT" not in sql


def test_busca_com_tag_e_autor_nao_usa_distinct():
    """Filtros por tag e autor não duplicam linhas nem exigem DISTINCT."""
    sql = _sql_postgres(
        query="python", tag_slug="python", author_slug="equipe-e-seller"
    )
    assert "DISTINCT" not in sql
    assert "ORDER BY CASE" in sql


async def test_busca_por_tag_nao_repete_produto(client):
    """Produto com várias tags aparece uma vez só no filtro por uma delas."""
    response = await client.get("/api/v1/products?q=python&tag=python")
    assert response.status_code == 200
    slugs = []
    for item in response.json():
        slugs.append(item["slug"])
    assert len(slugs) == len(set(slugs))
