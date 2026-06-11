"""Serviço de avaliações: criar (comprador verificado) e listar (async)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.catalog.models import Product
from app.entitlement.models import Entitlement
from app.reviews.models import Review, ReviewStatus


class ReviewNotAllowed(Exception):
    """Levantada quando o usuário não comprou o e-book que tenta avaliar."""


class AlreadyReviewed(Exception):
    """Levantada quando o usuário já avaliou o e-book."""


class InvalidRating(Exception):
    """Levantada quando a nota está fora do intervalo 1..5."""


class ReviewService:
    """Cria e lista avaliações; exige posse (comprador verificado) para criar."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção."""
        self.session = session

    async def create(
        self, user_id: int, product_slug: str, rating: int, comment: str
    ) -> Review:
        """Cria a avaliação; valida nota, posse e unicidade."""
        if rating < 1 or rating > 5:
            raise InvalidRating("a nota deve estar entre 1 e 5")
        product = await self._product_by_slug(product_slug)
        if not await self._owns(user_id, product.id):
            raise ReviewNotAllowed(product_slug)
        if await self._already_reviewed(user_id, product.id):
            raise AlreadyReviewed(product_slug)
        review = Review(
            product_id=product.id, user_id=user_id, rating=rating, comment=comment
        )
        self.session.add(review)
        await self.session.flush()
        return review

    async def list_for_product(
        self, product_slug: str, skip: int = 0, limit: int = 10
    ) -> list[dict]:
        """Lista as avaliações de um produto (com autor e data)."""
        statement = (
            select(Review.rating, Review.comment, User.email, Review.created_at)
            .join(User, User.id == Review.user_id)
            .join(Product, Product.id == Review.product_id)
            .where(
                Product.slug == product_slug,
                Review.status == ReviewStatus.APPROVED,
            )
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows = (await self.session.execute(statement)).all()
        reviews: list[dict] = []
        for row in rows:
            reviews.append(
                {
                    "rating": row[0],
                    "comment": row[1],
                    "author": row[2].split("@")[0],
                    "created_at": row[3].isoformat() if row[3] is not None else None,
                }
            )
        return reviews

    async def _product_by_slug(self, slug: str) -> Product:
        """Busca o produto pelo slug; levanta ReviewNotAllowed se inexistente."""
        result = await self.session.scalars(
            select(Product).where(Product.slug == slug)
        )
        product = result.first()
        if product is None:
            raise ReviewNotAllowed(slug)
        return product

    async def _owns(self, user_id: int, product_id: int) -> bool:
        """Verifica se o usuário possui o produto (comprador verificado)."""
        result = await self.session.scalars(
            select(Entitlement).where(
                Entitlement.user_id == user_id,
                Entitlement.product_id == product_id,
            )
        )
        return result.first() is not None

    async def _already_reviewed(self, user_id: int, product_id: int) -> bool:
        """Verifica se o usuário já avaliou o produto."""
        result = await self.session.scalars(
            select(Review).where(
                Review.user_id == user_id,
                Review.product_id == product_id,
            )
        )
        return result.first() is not None


class ReviewAdminLister:
    """Lista avaliações para a área administrativa com filtro por status."""

    _PAGE_SIZE_MAX = 100

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    def _base_statement(
        self, status: str | None, product_id: int | None = None
    ) -> object:
        """Constrói statement base com filtros opcionais de status e produto."""
        stmt = select(Review)
        if status is not None:
            try:
                stmt = stmt.where(Review.status == ReviewStatus(status))
            except ValueError:
                return None
        if product_id is not None:
            stmt = stmt.where(Review.product_id == product_id)
        return stmt

    async def list_reviews(
        self,
        page: int,
        page_size: int,
        status: str | None = None,
        product_id: int | None = None,
    ) -> list[Review]:
        """Retorna página de avaliações (mais recentes primeiro).

        Filtros opcionais: status (pending, approved, rejected) e product_id.
        """
        effective_size = min(page_size, self._PAGE_SIZE_MAX)
        stmt = self._base_statement(status, product_id)
        if stmt is None:
            return []
        stmt = (
            stmt.order_by(Review.id.desc())
            .offset((page - 1) * effective_size)
            .limit(effective_size)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def count_reviews(
        self, status: str | None = None, product_id: int | None = None
    ) -> int:
        """Retorna o total de avaliações com filtros aplicados."""
        from sqlalchemy import func as sa_func

        base = self._base_statement(status, product_id)
        if base is None:
            return 0
        count_stmt = select(sa_func.count()).select_from(base.subquery())
        result = await self.session.scalar(count_stmt)
        return int(result or 0)


class ReviewNotFound(Exception):
    """Levantada quando a avaliação não é encontrada pelo ID."""


class InvalidModerationStatus(Exception):
    """Levantada quando o status de moderação enviado não é válido."""


class ReviewModerator:
    """Modera avaliações (staff/admin): aprova ou rejeita."""

    _ALLOWED_STATUSES = {s.value for s in ReviewStatus}

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção."""
        self.session = session

    async def moderate(self, review_id: int, status: str) -> Review:
        """Aplica o status de moderação à avaliação.

        Levanta InvalidModerationStatus para status não reconhecido.
        Levanta ReviewNotFound se o ID não existir.
        """
        if status not in self._ALLOWED_STATUSES:
            raise InvalidModerationStatus(status)
        result = await self.session.scalars(
            select(Review).where(Review.id == review_id)
        )
        review = result.first()
        if review is None:
            raise ReviewNotFound(review_id)
        review.status = ReviewStatus(status)
        await self.session.flush()
        return review
