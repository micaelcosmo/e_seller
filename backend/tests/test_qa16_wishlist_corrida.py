"""Regressão QAF-16: favoritar é idempotente também na corrida (cliques simultâneos).

Spec: `.spec/unit/backend/wishlist/service_wishlist.md` ("`add` idempotente") e
`.spec/enrichment/roadmap-qaf.md` (QAF-16). O serviço conferia e depois inseria:
duas requisições ao mesmo tempo viam "não existe", e a segunda estourava a UNIQUE
(500 no Postgres). O teste força a corrida: a conferência diz "não existe" com o
item já gravado.
"""

from app.accounts.models import User, UserRole
from app.catalog.models import Product
from app.security.passwords import PasswordHasher
from app.wishlist.services import WishlistService


async def _usuario(db_session) -> int:
    """Comprador de teste."""
    hasher = PasswordHasher(iterations=1000)
    usuario = User(
        email="qa16@x.com", password_hash=hasher.hash("pw"), role=UserRole.CUSTOMER
    )
    db_session.add(usuario)
    await db_session.commit()
    return usuario.id


async def test_segundo_add_na_corrida_nao_quebra(db_session, monkeypatch):
    """Com o item já gravado e a conferência dizendo que não, `add` não levanta erro."""
    user_id = await _usuario(db_session)
    servico = WishlistService(db_session)
    await servico.add(user_id, "python-na-pratica")
    await db_session.commit()

    async def conferencia_atrasada(wishlist_id, product_id):
        """Simula a outra requisição que conferiu antes da primeira gravar."""
        return False

    monkeypatch.setattr(servico, "_has_item", conferencia_atrasada)
    await servico.add(user_id, "python-na-pratica")
    await db_session.commit()

    itens = await WishlistService(db_session).items(user_id)
    slugs = []
    for produto in itens:
        assert isinstance(produto, Product)
        slugs.append(produto.slug)
    assert slugs == ["python-na-pratica"]
