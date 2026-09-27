"""Model de avaliação (Review): nota e comentário de um comprador."""

import enum
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ReviewStatus(enum.Enum):
    """Estado de moderação de uma avaliação."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Review(Base):
    """Avaliação de um e-book por um usuário (1 por user/product)."""

    __tablename__ = "review"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_review_user_product"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="check_review_rating_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    rating: Mapped[int] = mapped_column()
    comment: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus),
        default=ReviewStatus.PENDING,
        server_default=ReviewStatus.PENDING.name,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
