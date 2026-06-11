"""Model de posse (Entitlement): o usuário possui o e-book perpetuamente."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Entitlement(Base):
    """Posse perpétua de um e-book por um usuário (1 por user/product)."""

    __tablename__ = "entitlement"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_entitlement_user_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_item.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
