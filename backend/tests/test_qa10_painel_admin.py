"""Regressão QAF-10/11/14: login do painel com CSRF, moderação e /comprar.

Spec: `.spec/enrichment/roadmap-qaf.md`. O CSRF (double-submit) exige `csrf_token`
em todo POST fora de `/api/`; o formulário do SQLAdmin não o enviava e o login
respondia 403. A correção mantém a proteção: as páginas do painel carregam um
script que copia o token do cookie para os formulários e para o jQuery.
"""

from datetime import UTC, datetime

from app.accounts.models import User, UserRole
from app.admin.views import ReviewAdmin
from app.reviews.models import Review
from app.security.passwords import PasswordHasher


async def _admin(db_session) -> None:
    """Conta de administrador com senha conhecida."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="qa10-admin@x.com",
            password_hash=hasher.hash("pw"),
            role=UserRole.ADMIN,
        )
    )
    await db_session.commit()


async def test_pagina_de_login_do_painel_leva_o_script_de_csrf(client):
    """O HTML do login traz o script que põe `csrf_token` nos formulários."""
    resposta = await client.get("/admin/login")
    assert resposta.status_code == 200
    assert "csrf_token" in resposta.text
    assert "csrftoken" in resposta.text


async def test_login_do_painel_com_token_do_cookie_entra(client, db_session):
    """Com o token do cookie no formulário (como o script faz), o login entra."""
    await _admin(db_session)
    await client.get("/admin/login")
    token = client.cookies.get("csrftoken")
    assert token
    resposta = await client.post(
        "/admin/login",
        data={"username": "qa10-admin@x.com", "password": "pw", "csrf_token": token},
    )
    assert resposta.status_code in (302, 303)
    assert resposta.headers["location"].rstrip("/").endswith("/admin")


async def test_login_do_painel_sem_token_continua_barrado(client, db_session):
    """Sem o token, o CSRF continua recusando (a proteção não foi desligada)."""
    await _admin(db_session)
    await client.get("/admin/login")
    resposta = await client.post(
        "/admin/login", data={"username": "qa10-admin@x.com", "password": "pw"}
    )
    assert resposta.status_code == 403


def test_lista_de_avaliacoes_mostra_comentario_e_status():
    """A moderação no painel enxerga o comentário e o status de cada avaliação."""
    colunas = []
    for coluna in ReviewAdmin.column_list:
        colunas.append(getattr(coluna, "key", str(coluna)))
    assert "comment" in colunas
    assert "status" in colunas
    nomes = []
    for filtro in ReviewAdmin.column_filters:
        nomes.append(filtro.parameter_name)
    assert "status" in nomes


async def test_comprar_da_vitrine_com_csrf_cria_pedido(client):
    """POST /comprar (vitrine do backend) com token cria o pedido e vai ao simulador."""
    await client.get("/")
    token = client.cookies.get("csrftoken")
    resposta = await client.post(
        "/comprar",
        data={"slug": "python-na-pratica", "email": "qa14@x.com", "csrf_token": token},
    )
    assert resposta.status_code == 303
    assert "/pay/simulate/" in resposta.headers["location"]


async def _entrar_no_painel(client, db_session) -> None:
    """Admin logado no SQLAdmin pelo formulário (com o token CSRF do cookie)."""
    await _admin(db_session)
    await client.get("/admin/login")
    token = client.cookies.get("csrftoken")
    await client.post(
        "/admin/login",
        data={"username": "qa10-admin@x.com", "password": "pw", "csrf_token": token},
    )


async def test_lista_de_avaliacoes_do_painel_renderiza_com_comentario(
    client, db_session
):
    """A página da lista abre (200) e mostra o comentário da avaliação."""
    hasher = PasswordHasher(iterations=1000)
    autor = User(
        email="qa11-autor@x.com",
        password_hash=hasher.hash("pw"),
        role=UserRole.CUSTOMER,
    )
    db_session.add(autor)
    await db_session.commit()
    db_session.add(
        Review(product_id=1, user_id=autor.id, rating=5, comment="qa11-fila")
    )
    await db_session.commit()
    await _entrar_no_painel(client, db_session)
    resposta = await client.get("/admin/review/list")
    assert resposta.status_code == 200
    assert "qa11-fila" in resposta.text
    filtrada = await client.get("/admin/review/list?status=PENDING")
    assert filtrada.status_code == 200
    assert "qa11-fila" in filtrada.text


def test_lista_de_avaliacoes_resume_comentario_e_data():
    """Comentário longo e data completa não estouram a largura da lista do painel."""
    avaliacao = Review(
        product_id=1,
        user_id=1,
        rating=5,
        comment="x" * 200,
        created_at=datetime(2026, 9, 27, 8, 47, 14, 435016, tzinfo=UTC),
    )
    resumo = ReviewAdmin.column_formatters[Review.comment](avaliacao, "comment")
    data = ReviewAdmin.column_formatters[Review.created_at](avaliacao, "created_at")
    assert len(resumo) <= 61
    assert resumo.endswith("…")
    assert data == "27/09/2026 08:47"


async def test_listas_do_painel_nao_estouram_a_largura_da_pagina(client):
    """O template do painel traz a regra que faz a tabela rolar dentro do card."""
    resposta = await client.get("/admin/login")
    assert ".d-flex > .flex-grow-1 { min-width: 0; }" in resposta.text
