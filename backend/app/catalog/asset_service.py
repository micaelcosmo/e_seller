"""Serviço de ativos do produto: arquivos (formatos) e imagens (capa/galeria)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import (
    Product,
    ProductFile,
    ProductFileFormat,
    ProductImage,
)


class ProductAssetNotFound(Exception):
    """Levantada quando o produto-alvo de um ativo não é encontrado."""


class ProductAssetService:
    """Adiciona e consulta arquivos e imagens vinculados a um produto."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção de dependência."""
        self.session = session

    async def add_file(
        self,
        product_id: int,
        file_format: ProductFileFormat,
        storage_key: str,
        version: str = "1",
        byte_size: int = 0,
        is_primary: bool = False,
    ) -> ProductFile:
        """Vincula um arquivo (formato/versão) a um produto existente."""
        await self._require_product(product_id)
        if is_primary:
            await self._clear_primary(product_id)
        product_file = ProductFile(
            product_id=product_id,
            file_format=file_format,
            storage_key=storage_key,
            version=version,
            byte_size=byte_size,
            is_primary=is_primary,
        )
        self.session.add(product_file)
        await self.session.flush()
        return product_file

    async def add_image(
        self,
        product_id: int,
        url: str,
        alt_text: str = "",
        position: int = 0,
        is_cover: bool = False,
    ) -> ProductImage:
        """Vincula uma imagem (capa ou galeria) a um produto existente."""
        product = await self._require_product(product_id)
        if is_cover:
            await self._clear_cover(product_id)
            product.cover_url = url
        image = ProductImage(
            product_id=product_id,
            url=url,
            alt_text=alt_text,
            position=position,
            is_cover=is_cover,
        )
        self.session.add(image)
        await self.session.flush()
        return image

    async def list_files(self, product_id: int) -> list[ProductFile]:
        """Lista os arquivos de um produto (primário primeiro)."""
        statement = (
            select(ProductFile)
            .where(ProductFile.product_id == product_id)
            .order_by(ProductFile.is_primary.desc(), ProductFile.id)
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def list_images(self, product_id: int) -> list[ProductImage]:
        """Lista as imagens de um produto (capa primeiro, depois por posição)."""
        statement = (
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.is_cover.desc(), ProductImage.position)
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def _require_product(self, product_id: int) -> Product:
        """Garante que o produto existe; levanta ProductAssetNotFound se ausente."""
        result = await self.session.scalars(
            select(Product).where(Product.id == product_id)
        )
        product = result.first()
        if product is None:
            raise ProductAssetNotFound(product_id)
        return product

    async def _clear_primary(self, product_id: int) -> None:
        """Remove a marca de primário dos demais arquivos do produto."""
        result = await self.session.scalars(
            select(ProductFile).where(
                ProductFile.product_id == product_id,
                ProductFile.is_primary.is_(True),
            )
        )
        for product_file in result.all():
            product_file.is_primary = False

    async def _clear_cover(self, product_id: int) -> None:
        """Remove a marca de capa das demais imagens do produto."""
        result = await self.session.scalars(
            select(ProductImage).where(
                ProductImage.product_id == product_id,
                ProductImage.is_cover.is_(True),
            )
        )
        for image in result.all():
            image.is_cover = False
