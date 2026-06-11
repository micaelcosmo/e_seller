"""Models de wishlist: Wishlist e WishlistItem."""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Wishlist(Base):
    """Lista de desejos de um usuário (1 por usuário)."""

    __tablename__ = "wishlist"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True, index=True)


class WishlistItem(Base):
    """Item da lista de desejos (1 por produto)."""

    __tablename__ = "wishlist_item"
    __table_args__ = (
        UniqueConstraint("wishlist_id", "product_id", name="uq_wishlist_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    wishlist_id: Mapped[int] = mapped_column(ForeignKey("wishlist.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
