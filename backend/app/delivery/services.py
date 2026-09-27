"""Serviços de entrega: emissão, validação e streaming de downloads (async)."""

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models import Product, ProductFile
from app.core.clock import Clock
from app.delivery.models import DownloadGrant
from app.orders.models import OrderItem
from app.security.storage import FileMissing, ProtectedStorage
from app.security.tokens import TokenFactory


class GrantNotFound(Exception):
    """Levantada quando o token de download não existe."""


class GrantExpired(Exception):
    """Levantada quando o link de download está expirado."""


class DownloadLimitReached(Exception):
    """Levantada quando o limite de downloads foi atingido."""


class DownloadIssuer:
    """Emite concessões de download (DownloadGrant) para itens pagos."""

    def __init__(
        self,
        session: AsyncSession,
        token_factory: TokenFactory,
        clock: Clock,
        ttl_days: int = 7,
        max_downloads: int = 5,
    ) -> None:
        """Recebe dependências e regras de expiração/limite por injeção."""
        self.session = session
        self.token_factory = token_factory
        self.clock = clock
        self.ttl_days = ttl_days
        self.max_downloads = max_downloads

    async def issue_for(self, order_item: OrderItem) -> DownloadGrant:
        """Cria e persiste um DownloadGrant para o item de pedido informado."""
        grant = DownloadGrant(
            order_item_id=order_item.id,
            product_id=order_item.product_id,
            token=self.token_factory.generate(),
            expires_at=self.clock.now() + timedelta(days=self.ttl_days),
            max_downloads=self.max_downloads,
            download_count=0,
        )
        self.session.add(grant)
        await self.session.flush()
        return grant


class GrantValidator:
    """Valida e consome um token de download (expiração e limite)."""

    def __init__(self, session: AsyncSession, clock: Clock) -> None:
        """Recebe a sessão e o relógio por injeção."""
        self.session = session
        self.clock = clock

    async def consume(self, token: str) -> DownloadGrant:
        """Valida o token, incrementa o contador e retorna o grant."""
        statement = select(DownloadGrant).where(DownloadGrant.token == token)
        result = await self.session.scalars(statement)
        grant = result.first()
        if grant is None:
            raise GrantNotFound(token)
        if self.clock.now() >= self.clock.as_naive_utc(grant.expires_at):
            raise GrantExpired(token)
        if grant.download_count >= grant.max_downloads:
            raise DownloadLimitReached(token)
        grant.download_count = grant.download_count + 1
        await self.session.flush()
        return grant


class GrantRevoker:
    """Invalida concessões de download de um pedido (anti-pirataria no estorno)."""

    def __init__(self, session: AsyncSession, clock: Clock) -> None:
        """Recebe a sessão e o relógio por injeção de dependência."""
        self.session = session
        self.clock = clock

    async def revoke_for_order(self, order) -> int:
        """Expira os grants ativos dos itens do pedido; retorna quantos invalidou.

        Não apaga o registro (auditoria): apenas antecipa `expires_at` para agora,
        de modo que qualquer download futuro falhe com GrantExpired.
        """
        now = self.clock.now()
        revoked = 0
        for item in order.items:
            result = await self.session.scalars(
                select(DownloadGrant).where(
                    DownloadGrant.order_item_id == item.id,
                    DownloadGrant.expires_at > now,
                )
            )
            for grant in result.all():
                grant.expires_at = now
                revoked = revoked + 1
        await self.session.flush()
        return revoked


class FileStreamer:
    """Lê o arquivo do e-book a partir do armazenamento protegido."""

    def __init__(self, session: AsyncSession, storage: ProtectedStorage) -> None:
        """Recebe a sessão e o armazenamento protegido por injeção."""
        self.session = session
        self.storage = storage

    async def read_for_grant(self, grant: DownloadGrant) -> tuple[bytes, str]:
        """Retorna (conteúdo, nome de arquivo) do produto associado ao grant.

        A fonte é o arquivo primário (`ProductFile`), que é o que o upload do admin
        grava; `Product.file_name` fica como alternativa para produtos antigos.
        """
        product = await self.session.get(Product, grant.product_id)
        if product is None:
            raise FileMissing(str(grant.product_id))
        primary = await self._primary_file(product.id)
        if primary is not None:
            content = self.storage.read_bytes(primary.storage_key)
            extension = primary.storage_key.rsplit(".", 1)[-1].lower()
            return content, product.slug + "." + extension
        if not product.file_name:
            raise FileMissing(str(grant.product_id))
        content = self.storage.read_bytes(product.file_name)
        return content, product.file_name

    async def _primary_file(self, product_id: int) -> ProductFile | None:
        """Arquivo primário do produto (o mais recente, se houver mais de um)."""
        result = await self.session.scalars(
            select(ProductFile)
            .where(
                ProductFile.product_id == product_id,
                ProductFile.is_primary.is_(True),
            )
            .order_by(ProductFile.id.desc())
        )
        return result.first()
