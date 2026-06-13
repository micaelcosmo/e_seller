"""Serviços de AAA (Authentication/Authorization/Accounting) — enrichment.

Contém: UserActivityLogService, ApiKeyService, TOTPService.
"""

import base64
import hashlib
import logging
import secrets
from datetime import UTC, datetime

import pyotp
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import ApiKey, User, UserActivityLog

_logger = logging.getLogger(__name__)


class UserActivityLogService:
    """Registra ações auditáveis do usuário (accounting).

    Silencia exceções internas para não interromper o fluxo principal.
    Eventos: 'login', 'purchase', 'download', 'profile_update', '2fa_enrolled'.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão assíncrona do banco."""
        self.session = session

    async def log(
        self,
        event_type: str,
        user_id: int | None = None,
        **meta: object,
    ) -> None:
        """Persiste um evento de atividade. Não propaga exceções."""
        try:
            entry = UserActivityLog(
                user_id=user_id,
                event_type=event_type,
                meta=dict(meta) if meta else None,
            )
            self.session.add(entry)
            await self.session.commit()
        except Exception as exc:
            _logger.warning("activity_log_failed event=%s error=%s", event_type, exc)
            await self.session.rollback()

    async def list_for_user(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[UserActivityLog]:
        """Retorna as atividades recentes do usuário, ordenadas por data desc."""
        result = await self.session.scalars(
            select(UserActivityLog)
            .where(UserActivityLog.user_id == user_id)
            .order_by(UserActivityLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.all())


class ApiKeyService:
    """Gerencia chaves de API para autenticação programática.

    A chave crua (raw_key) é exibida apenas na criação; o hash SHA-256 é persistido.
    """

    _PREFIX_LENGTH = 8

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão assíncrona do banco."""
        self.session = session

    def _hash_key(self, raw_key: str) -> str:
        """Retorna o hash SHA-256 da chave crua (hex)."""
        return hashlib.sha256(raw_key.encode()).hexdigest()

    async def generate(
        self,
        user_id: int,
        name: str,
        expires_at: datetime | None = None,
    ) -> tuple[str, ApiKey]:
        """Cria uma nova API Key; retorna (chave_crua, registro).

        A chave crua deve ser exibida ao usuário UMA ÚNICA VEZ.
        """
        raw = secrets.token_urlsafe(32)
        prefix = raw[: self._PREFIX_LENGTH]
        key_hash = self._hash_key(raw)
        key = ApiKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            prefix=prefix,
            expires_at=expires_at,
        )
        self.session.add(key)
        await self.session.commit()
        await self.session.refresh(key)
        return raw, key

    async def authenticate(self, raw_key: str) -> User | None:
        """Autentica via chave crua; retorna o usuário ou None.

        Atualiza last_used_at e valida is_active + expires_at.
        """
        key_hash = self._hash_key(raw_key)
        result = await self.session.scalars(
            select(ApiKey).where(
                ApiKey.key_hash == key_hash,
                ApiKey.is_active.is_(True),
            )
        )
        api_key = result.first()
        if api_key is None:
            return None
        now = datetime.now(tz=UTC)
        if api_key.expires_at is not None:
            exp = api_key.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=UTC)
            if exp < now:
                return None
        api_key.last_used_at = now
        await self.session.commit()
        user_result = await self.session.scalars(
            select(User).where(User.id == api_key.user_id, User.is_active.is_(True))
        )
        return user_result.first()

    async def revoke(self, key_id: int, user_id: int) -> bool:
        """Revoga a chave. True se encontrada; False se não pertence ao usuário."""
        result = await self.session.scalars(
            select(ApiKey).where(
                ApiKey.id == key_id,
                ApiKey.user_id == user_id,
            )
        )
        key = result.first()
        if key is None:
            return False
        key.is_active = False
        await self.session.commit()
        return True

    async def list_keys(self, user_id: int) -> list[ApiKey]:
        """Lista as chaves ativas do usuário (sem expor o hash)."""
        result = await self.session.scalars(
            select(ApiKey)
            .where(ApiKey.user_id == user_id, ApiKey.is_active.is_(True))
            .order_by(ApiKey.created_at.desc())
        )
        return list(result.all())


class TOTPService:
    """Serviço de autenticação TOTP (RFC 6238) para 2FA.

    O secret TOTP é cifrado com AES-256-GCM usando a chave configurada nas settings,
    evitando que o secret fique em texto claro no banco de dados.
    """

    def __init__(self, encryption_key_b64: str) -> None:
        """Recebe a chave AES-GCM em base64 (32 bytes = AES-256)."""
        self._key = base64.b64decode(encryption_key_b64)

    def generate_secret(self) -> str:
        """Gera um novo secret TOTP (base32, 32 chars)."""
        return pyotp.random_base32()

    def generate_provisioning_uri(self, secret: str, email: str) -> str:
        """Retorna a URI otpauth:// para configuração em apps autenticadores."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name="e_seller")

    def verify(self, secret: str, code: str, window: int = 1) -> bool:
        """Verifica se o código TOTP é válido para o secret dado."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=window)

    def encrypt_secret(self, secret: str) -> str:
        """Cifra o secret TOTP com AES-256-GCM; retorna base64(nonce + ciphertext)."""
        aesgcm = AESGCM(self._key)
        nonce = secrets.token_bytes(12)
        ciphertext = aesgcm.encrypt(nonce, secret.encode(), None)
        return base64.b64encode(nonce + ciphertext).decode()

    def decrypt_secret(self, enc: str) -> str:
        """Decifra o secret TOTP cifrado; retorna o secret original."""
        raw = base64.b64decode(enc)
        nonce = raw[:12]
        ciphertext = raw[12:]
        aesgcm = AESGCM(self._key)
        return aesgcm.decrypt(nonce, ciphertext, None).decode()
