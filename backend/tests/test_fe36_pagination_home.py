"""Testes FE-36: paginação Próxima/Anterior na vitrine."""

from __future__ import annotations


async def test_home_tem_btn_prev(client) -> None:
    """Home deve renderizar botão Anterior (#btn-prev)."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert 'id="btn-prev"' in resp.text


async def test_home_tem_btn_next(client) -> None:
    """Home deve renderizar botão Próxima (#btn-next)."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert 'id="btn-next"' in resp.text


async def test_home_tem_changepage_js(client) -> None:
    """Home deve conter a função changePage no script."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "changePage" in resp.text
