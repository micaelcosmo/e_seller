"""Models de contas: User, LoginAttempt e papéis (RBAC mínimo)."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class UserRole(enum.StrEnum):
    """Papéis de usuário (RBAC mínimo)."""

    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"


class User(Base):
    """Conta de usuário (comprador ou operador)."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(160), default="")
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Campo de retenção LGPD: quando preenchido, a conta foi anonimizada.
    # Email é substituído por hash; outros campos pessoais são apagados.
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )


class LoginAttempt(Base):
    """Registro de tentativa de login (auditoria de segurança).

    Inclui sucessos e falhas; ip_address pode ser vazio em testes sem proxy.
    """

    __tablename__ = "login_attempt"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), index=True)
    # user_id nulo quando o login falhou (usuário não existe).
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id"), nullable=True, index=True
    )
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    ip_address: Mapped[str] = mapped_column(String(45), default="")
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
