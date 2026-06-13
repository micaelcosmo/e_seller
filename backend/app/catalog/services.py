"""Serviços de catálogo: consultas e cadastro dinâmico de e-books (async)."""

from __future__ import annotations

import asyncio
import json
import urllib.request
from decimal import Decimal
from typing import Protocol
from urllib.parse import urlparse

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import update as sql_update

from app.catalog.models import Product, ProductStatus
from app.catalog.repository import ProductRepository
from app.catalog.schemas import ProductDraftIn, ProductUpdateIn
from app.catalog.taxonomy_service import TaxonomyService
from app.core.text import Slugifier
from app.orders.models import Order, OrderItem, OrderStatus


class ProductNotFound(Exception):
    """Levantada quando um produto publicado não é encontrado."""


class InvalidManifestUrl(Exception):
    """Levantada quando a URL de importação é inválida ou não permitida."""


class ManifestError(Exception):
    """Levantada quando o manifest importado não pôde ser lido/parseado."""


class ProductCatalog:
    """Consulta produtos do catálogo (apenas publicados ao público)."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção de dependência."""
        self.session = session
        self.repo = ProductRepository(session)

    async def list_published(
        self,
        query: str | None = None,
        skip: int = 0,
        limit: int = 20,
        tag_slug: str | None = None,
        author_slug: str | None = None,
        sort: str | None = None,
        featured: bool | None = None,
        price_min: Decimal | None = None,
        price_max: Decimal | None = None,
    ) -> list[Product]:
        """Lista produtos publicados com paginação, busca, filtros e ordenação."""
        products = await self.repo.list_published(
            query, skip, limit, tag_slug, author_slug, sort, featured,
            price_min, price_max,
        )
        await self._attach_review_counts(products)
        return products

    async def _attach_review_counts(self, products: list[Product]) -> None:
        """Popula review_count e avg_rating em cada produto com uma única query.

        Considera apenas reviews com status APPROVED. Produtos sem reviews
        aprovadas recebem review_count=0 e avg_rating=0.0. Evita N+1.
        """
        from app.reviews.models import Review, ReviewStatus

        if not products:
            return
        ids = [p.id for p in products]
        stmt = (
            select(
                Review.product_id,
                func.count(Review.id).label("cnt"),
                func.avg(Review.rating).label("avg_rating"),
            )
            .where(Review.product_id.in_(ids), Review.status == ReviewStatus.APPROVED)
            .group_by(Review.product_id)
        )
        rows = (await self.session.execute(stmt)).all()
        counts = {}
        averages = {}
        for row in rows:
            counts[row.product_id] = row.cnt
            # avg vem como Decimal/None; arredonda para 1 casa para exibição.
            average = round(float(row.avg_rating), 1) if row.avg_rating else 0.0
            averages[row.product_id] = average
        for product in products:
            product.review_count = counts.get(product.id, 0)
            product.avg_rating = averages.get(product.id, 0.0)

    async def count_published(
        self,
        query: str | None = None,
        tag_slug: str | None = None,
        author_slug: str | None = None,
        price_min: Decimal | None = None,
        price_max: Decimal | None = None,
    ) -> int:
        """Conta produtos publicados com os mesmos filtros da listagem."""
        return await self.repo.count_published(
            query, tag_slug, author_slug, price_min, price_max
        )

    async def get_related(self, slug: str, limit: int = 4) -> list[Product]:
        """Retorna produtos relacionados ao slug informado (mesmo autor/tag).

        Retorna lista vazia se o produto não for encontrado.
        """
        product = await self.repo.get_published_by_slug(slug)
        if product is None:
            return []
        return await self.repo.find_related(product, limit)

    async def get_by_slug(self, slug: str) -> Product:
        """Retorna o produto publicado pelo slug; levanta ProductNotFound se ausente.

        Incrementa view_count de forma atômica (UPDATE sem re-fetch).
        """
        product = await self.repo.get_published_by_slug(slug)
        if product is None:
            raise ProductNotFound(slug)
        await self.session.execute(
            sql_update(Product)
            .where(Product.id == product.id)
            .values(view_count=Product.view_count + 1)
        )
        await self._attach_review_counts([product])
        return product


class ProductDeletionNotAllowed(Exception):
    """Levantada ao tentar excluir um produto publicado com pedidos pagos."""


class ProductEditor:
    """Edita campos básicos de um e-book já cadastrado."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção."""
        self.session = session

    async def update(self, slug: str, data: ProductUpdateIn) -> Product:
        """Aplica as alterações ao produto e retorna o objeto atualizado.

        Apenas campos explicitamente fornecidos (não None) são modificados.
        Levanta ProductNotFound se o slug não existir.
        """
        result = await self.session.scalars(
            select(Product).where(Product.slug == slug)
        )
        product = result.first()
        if product is None:
            raise ProductNotFound(slug)
        if data.title is not None:
            product.title = data.title
        if data.author is not None:
            product.author = data.author
        if data.description is not None:
            product.description = data.description
        if data.price is not None:
            product.price = data.price
        if data.cover_url is not None:
            product.cover_url = data.cover_url
        if data.featured is not None:
            product.featured = data.featured
        await self.session.flush()
        return product


class ProductDeleter:
    """Remove um e-book do catálogo permanentemente."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção."""
        self.session = session

    async def delete(self, slug: str) -> None:
        """Exclui o produto identificado pelo slug.

        Levanta ProductNotFound se o slug não existir.
        Levanta ProductDeletionNotAllowed se houver pedido pago vinculado.
        """
        result = await self.session.scalars(
            select(Product).where(Product.slug == slug)
        )
        product = result.first()
        if product is None:
            raise ProductNotFound(slug)
        paid_check = await self.session.scalars(
            select(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .where(
                OrderItem.product_id == product.id,
                Order.status == OrderStatus.PAID,
            )
            .limit(1)
        )
        if paid_check.first() is not None:
            raise ProductDeletionNotAllowed(slug)
        await self.session.delete(product)
        await self.session.flush()


class InvalidStatus(Exception):
    """Levantada quando o status solicitado é inválido."""


class ProductPublisher:
    """Altera o status de publicação de um e-book (admin)."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção."""
        self.session = session

    async def set_status(self, slug: str, status: str) -> Product:
        """Define o status (published/draft) de um produto pelo slug.

        Levanta ProductNotFound se o slug não existir.
        Levanta InvalidStatus se o valor não for reconhecido.
        """
        allowed = {s.value for s in ProductStatus}
        if status not in allowed:
            raise InvalidStatus(status)
        result = await self.session.scalars(
            select(Product).where(Product.slug == slug)
        )
        product = result.first()
        if product is None:
            raise ProductNotFound(slug)
        product.status = ProductStatus(status)
        await self.session.flush()
        return product


class ManifestImporter(Protocol):
    """Contrato para importar um manifest (JSON) de e-book a partir de uma URL."""

    async def fetch_json(self, url: str) -> dict:
        """Baixa e retorna o JSON do manifest."""
        ...


class HttpManifestImporter:
    """Importador de manifest via HTTP(S) com proteção básica anti-SSRF (stdlib)."""

    _BLOCKED_HOSTS = ("localhost", "127.0.0.1", "0.0.0.0", "::1")

    def __init__(self, timeout: int = 10) -> None:
        """Define o timeout das requisições."""
        self.timeout = timeout

    async def fetch_json(self, url: str) -> dict:
        """Valida a URL e baixa o JSON (em thread, para não bloquear o loop)."""
        self._validate(url)
        raw = await asyncio.to_thread(self._fetch_sync, url)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ManifestError("JSON inválido") from error
        if not isinstance(data, dict):
            raise ManifestError("manifest deve ser um objeto JSON")
        return data

    def _validate(self, url: str) -> None:
        """Permite apenas http/https e bloqueia hosts locais (anti-SSRF)."""
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise InvalidManifestUrl("apenas http/https são permitidos")
        if parsed.hostname is None or parsed.hostname in self._BLOCKED_HOSTS:
            raise InvalidManifestUrl("host não permitido")

    def _fetch_sync(self, url: str) -> bytes:
        """Faz a requisição HTTP síncrona e retorna o corpo."""
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=self.timeout) as response:  # noqa: S310
            return response.read()


class ProductRegistrar:
    """Cadastra e-books (rascunho) a partir de dados manuais, JSON ou link."""

    def __init__(self, session: AsyncSession, importer: ManifestImporter) -> None:
        """Recebe a sessão e o importador de manifest por injeção."""
        self.session = session
        self.importer = importer
        self.repo = ProductRepository(session)
        self.taxonomy = TaxonomyService(session)
        self._slugifier = Slugifier(fallback="ebook")

    async def from_fields(self, data: ProductDraftIn) -> Product:
        """Cria o e-book a partir de dados já validados (modo manual)."""
        return await self._create(data)

    async def from_json(self, payload: dict) -> Product:
        """Valida um JSON colado e cria o e-book (modo JSON)."""
        data = ProductDraftIn.model_validate(payload)
        return await self._create(data)

    async def from_link(self, url: str) -> Product:
        """Importa um manifest de uma URL e cria o e-book (modo link)."""
        payload = await self.importer.fetch_json(url)
        data = ProductDraftIn.model_validate(payload)
        return await self._create(data)

    async def _create(self, data: ProductDraftIn) -> Product:
        """Cria e persiste o produto como rascunho, com slug único."""
        category_id = await self.repo.resolve_category_id(data.category_slug)
        slug = await self._unique_slug(data.title)
        product = Product(
            title=data.title,
            slug=slug,
            author=data.author,
            description=data.description,
            price=data.price,
            cover_url=data.cover_url,
            status=ProductStatus.DRAFT,
            category_id=category_id,
        )
        # Inicializa as coleções de ativos como carregadas (vazias) para que a
        # serialização posterior não dispare lazy-load implícito (proibido em async).
        product.files = []
        product.images = []
        # Anexa a taxonomia enquanto o produto ainda é transitório: assim o
        # SQLAlchemy async não dispara um lazy-load implícito da coleção.
        await self.taxonomy.apply_to_product(
            product,
            authors=data.authors,
            publisher=data.publisher,
            series=data.series,
            tags=data.tags,
        )
        self.session.add(product)
        await self.session.flush()
        return product

    async def _unique_slug(self, title: str) -> str:
        """Gera um slug único a partir do título (com sufixo numérico se colidir)."""
        base = self._slugifier.slugify(title)
        candidate = base
        suffix = 2
        while await self.repo.slug_exists(candidate):
            candidate = f"{base}-{suffix}"
            suffix = suffix + 1
        return candidate


class ProductViewReporter:
    """Consulta os produtos mais visualizados (admin)."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção de dependência."""
        self.session = session

    async def top_viewed(self, limit: int = 10) -> list[Product]:
        """Retorna os produtos com maior view_count em ordem decrescente."""
        result = await self.session.scalars(
            select(Product)
            .order_by(Product.view_count.desc())
            .limit(limit)
        )
        return list(result.all())
