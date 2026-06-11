"""Testes da taxonomia do catálogo: autores, editora, série e tags."""

from decimal import Decimal

from app.catalog.schemas import ProductDraftIn
from app.catalog.services import HttpManifestImporter, ProductRegistrar
from app.catalog.taxonomy_service import TaxonomyService


async def test_get_or_create_autor_idempotente(db_session):
    """Criar o mesmo autor duas vezes não duplica o registro."""
    taxonomy = TaxonomyService(db_session)
    primeiro = await taxonomy.get_or_create_author("Machado de Assis")
    segundo = await taxonomy.get_or_create_author("machado de assis")
    assert primeiro.id == segundo.id
    autores = await taxonomy.list_authors()
    repetidos = 0
    for autor in autores:
        if autor.slug == "machado-de-assis":
            repetidos = repetidos + 1
    assert repetidos == 1


async def test_cadastro_associa_taxonomia(db_session):
    """Cadastrar um e-book com taxonomia cria e associa autores, editora e tags."""
    registrar = ProductRegistrar(db_session, HttpManifestImporter())
    draft = ProductDraftIn(
        title="Dom Casmurro",
        price=Decimal("19.90"),
        authors=["Machado de Assis"],
        publisher="Garnier",
        series="Clássicos BR",
        tags=["romance", "brasil"],
    )
    product = await registrar.from_fields(draft)
    assert len(product.authors) == 1
    assert product.authors[0].slug == "machado-de-assis"
    assert len(product.tags) == 2
    assert product.publisher_id is not None
    assert product.series_id is not None


async def test_listagem_de_tags_endpoint(client, db_session):
    """O endpoint público de tags retorna as tags cadastradas."""
    registrar = ProductRegistrar(db_session, HttpManifestImporter())
    await registrar.from_fields(
        ProductDraftIn(
            title="Memórias Póstumas",
            price=Decimal("9.90"),
            tags=["romance"],
        )
    )
    await db_session.commit()
    resp = await client.get("/api/v1/tags")
    assert resp.status_code == 200
    slugs = []
    for item in resp.json():
        slugs.append(item["slug"])
    assert "romance" in slugs
