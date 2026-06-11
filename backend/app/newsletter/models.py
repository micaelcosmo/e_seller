"""Model de inscrito na newsletter."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class NewsletterSubscriber(Base):
    """Inscrito na newsletter (captação de marketing)."""

    __tablename__ = "newsletter_subscriber"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    unsubscribed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
