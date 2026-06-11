"""Testes de ativos do produto: arquivos (formatos) e imagens (capa/galeria)."""

from decimal import Decimal

import pytest
from sqlalchemy import select

from app.catalog.asset_service import ProductAssetNotFound, ProductAssetService
from app.catalog.models import Product, ProductFileFormat
from app.catalog.schemas import ProductDraftIn
from app.catalog.services import HttpManifestImporter, ProductRegistrar


async def _criar_produto(db_session) -> Product:
    """Cria um produto de apoio para os testes de ativos."""
    registrar = ProductRegistrar(db_session, HttpManifestImporter())
    return await registrar.from_fields(
        ProductDraftIn(title="E-book com Ativos", price=Decimal("10.00"))
    )


async def test_adicionar_arquivo_primario(db_session):
    """Adicionar um arquivo primário registra o formato e a marca de primário."""
    produto = await _criar_produto(db_session)
    assets = ProductAssetService(db_session)
    arquivo = await assets.add_file(
        produto.id,
        file_format=ProductFileFormat.PDF,
        storage_key="ativos.pdf",
        is_primary=True,
    )
    assert arquivo.is_primary is True
    arquivos = await assets.list_files(produto.id)
    assert len(arquivos) == 1
    assert arquivos[0].file_format == ProductFileFormat.PDF


async def test_segundo_primario_substitui_o_anterior(db_session):
    """Marcar um novo arquivo como primário desmarca o anterior."""
    produto = await _criar_produto(db_session)
    assets = ProductAssetService(db_session)
    await assets.add_file(
        produto.id, ProductFileFormat.PDF, "v1.pdf", is_primary=True
    )
    await assets.add_file(
        produto.id, ProductFileFormat.EPUB, "v1.epub", is_primary=True
    )
    primarios = 0
    for arquivo in await assets.list_files(produto.id):
        if arquivo.is_primary:
            primarios = primarios + 1
    assert primarios == 1


async def test_imagem_de_capa_atualiza_cover_url(db_session):
    """Adicionar imagem como capa atualiza o cover_url do produto."""
    produto = await _criar_produto(db_session)
    assets = ProductAssetService(db_session)
    await assets.add_image(
        produto.id, url="https://x/capa.png", alt_text="Capa", is_cover=True
    )
    result = await db_session.scalars(
        select(Product).where(Product.id == produto.id)
    )
    atualizado = result.first()
    assert atualizado.cover_url == "https://x/capa.png"


async def test_produto_inexistente_levanta_erro(db_session):
    """Anexar ativo a produto inexistente levanta ProductAssetNotFound."""
    assets = ProductAssetService(db_session)
    with pytest.raises(ProductAssetNotFound):
        await assets.add_file(999999, ProductFileFormat.TXT, "x.txt")
