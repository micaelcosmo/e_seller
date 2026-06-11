"""Model de faturamento: BillingProfile (dados fiscais para nota fiscal)."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class PersonType(enum.StrEnum):
    """Tipo de pessoa para fins fiscais (física ou jurídica)."""

    INDIVIDUAL = "individual"
    COMPANY = "company"


class BillingProfile(Base):
    """Perfil fiscal do usuário (um por usuário) usado para emitir nota fiscal."""

    __tablename__ = "billing_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), unique=True, index=True
    )
    person_type: Mapped[PersonType] = mapped_column(
        Enum(PersonType), default=PersonType.INDIVIDUAL
    )
    legal_name: Mapped[str] = mapped_column(String(200))
    document: Mapped[str] = mapped_column(String(14), index=True)
    address_line: Mapped[str] = mapped_column(String(200), default="")
    city: Mapped[str] = mapped_column(String(120), default="")
    state: Mapped[str] = mapped_column(String(2), default="")
    postal_code: Mapped[str] = mapped_column(String(8), default="")
    country: Mapped[str] = mapped_column(String(2), default="BR")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
