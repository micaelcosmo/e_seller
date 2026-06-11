"""Model de entrega: DownloadGrant (link temporário de download)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class DownloadGrant(Base):
    """Concessão temporária de download (token, expiração e limite)."""

    __tablename__ = "download_grant"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_item.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
    max_downloads: Mapped[int] = mapped_column(default=5)
    download_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DownloadLog(Base):
    """Registro de auditoria de cada download (anti-pirataria; IP em hash)."""

    __tablename__ = "download_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    download_grant_id: Mapped[int] = mapped_column(
        ForeignKey("download_grant.id"), index=True
    )
    ip_hash: Mapped[str] = mapped_column(String(64), default="")
    downloaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
