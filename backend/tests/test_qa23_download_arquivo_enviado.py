"""Regressão QAF-23: e-book cadastrado pelo admin é entregue pelo arquivo enviado.

Spec: `.spec/enrichment/roadmap-qaf.md` (QAF-23). O upload grava o arquivo como
`ProductFile` primário (`storage_key`), mas o download lia só `Product.file_name`
(preenchido apenas pelo seed): todo e-book novo respondia 404 "Arquivo indisponível".
"""

from datetime import datetime, timedelta
from decimal import Decimal

from app.catalog.models import Product, ProductFile, ProductFileFormat, ProductStatus
from app.delivery.models import DownloadGrant
from app.delivery.services import FileStreamer
from app.security.storage import ProtectedStorage


async def test_download_usa_o_arquivo_primario_enviado(db_session, settings):
    """Sem `file_name`, entrega o `ProductFile` primário, com nome amigável."""
    storage = ProtectedStorage(settings.storage_dir)
    storage.write_bytes("qa23-novo/abc.txt", b"qa-conteudo-do-ebook")
    produto = Product(
        title="QA23 Novo",
        slug="qa23-novo",
        author="QA",
        description="",
        price=Decimal("9.90"),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(produto)
    await db_session.flush()
    db_session.add(
        ProductFile(
            product_id=produto.id,
            file_format=ProductFileFormat.TXT,
            storage_key="qa23-novo/abc.txt",
            version="1",
            byte_size=20,
            is_primary=True,
        )
    )
    await db_session.commit()
    grant = DownloadGrant(
        order_item_id=0,
        product_id=produto.id,
        token="qa23-token",
        expires_at=datetime(2099, 1, 1) + timedelta(days=0),
        max_downloads=5,
        download_count=0,
    )
    conteudo, nome = await FileStreamer(db_session, storage).read_for_grant(grant)
    assert conteudo == b"qa-conteudo-do-ebook"
    assert nome == "qa23-novo.txt"
