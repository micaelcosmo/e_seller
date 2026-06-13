"""Models de contas: User, LoginAttempt, RevokedToken, UserActivityLog, ApiKey."""

import enum
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Index, String, func
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
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    # 2FA/TOTP: secret cifrado em AES-GCM (base64); nulo enquanto não ativado.
    totp_secret_enc: Mapped[str | None] = mapped_column(
        String(512), nullable=True, default=None
    )
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)


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


class RevokedToken(Base):
    """JWT revogado via logout. Verificado por get_current_user antes de autorizar.

    Limpeza periódica: registros com expires_at < now() podem ser purgados.
    """

    __tablename__ = "revoked_token"

    id: Mapped[int] = mapped_column(primary_key=True)
    # jti = JWT ID claim (UUID4 gerado no issue()).
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class UserActivityLog(Base):
    """Trilha de auditoria de ações do usuário (accounting).

    event_type: 'login', 'purchase', 'download', 'profile_update', '2fa_enrolled'.
    metadata: JSON livre; nunca incluir senha ou token completo.
    """

    __tablename__ = "user_activity_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    # user_id nulo para ações anônimas (compras sem login).
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id"), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    # metadata: dicionário livre; serializado como JSON.
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    __table_args__ = (
        # Índice composto para paginação eficiente por usuário.
        Index("ix_activity_user_created", "user_id", "created_at"),
    )


class ApiKey(Base):
    """Chave de API para autenticação programática (alternativa ao JWT).

    A chave crua (raw_key) é exibida apenas na criação; somente o hash SHA-256
    é persistido. Prefixo (8 chars) exibido nas listagens para identificação visual.
    """

    __tablename__ = "api_key"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    # Hash SHA-256 da chave crua; UNIQUE para evitar duplicatas.
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    # Prefixo visível ao usuário (8 chars iniciais do token).
    prefix: Mapped[str] = mapped_column(String(16))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
