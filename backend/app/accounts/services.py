"""Serviços de contas: autenticação e registro de usuários (async)."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import LoginAttempt, User, UserRole
from app.security.jwt import JwtService
from app.security.passwords import PasswordHasher


class InvalidCredentials(Exception):
    """Levantada quando e-mail/senha não conferem ou conta inativa."""


class EmailAlreadyUsed(Exception):
    """Levantada ao registrar um e-mail já existente."""


class Authenticator:
    """Autentica usuários e emite tokens; registra novos compradores."""

    def __init__(
        self,
        session: AsyncSession,
        hasher: PasswordHasher,
        tokens: JwtService,
    ) -> None:
        """Recebe sessão, hasher de senha e serviço de JWT por injeção."""
        self.session = session
        self.hasher = hasher
        self.tokens = tokens

    async def login(self, email: str, password: str) -> str:
        """Valida credenciais e retorna um JWT; levanta InvalidCredentials."""
        user = await self.get_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentials("credenciais inválidas")
        if not self.hasher.verify(password, user.password_hash):
            raise InvalidCredentials("credenciais inválidas")
        return self.tokens.issue(subject=user.email)

    async def register_customer(
        self, email: str, password: str, full_name: str = ""
    ) -> User:
        """Registra um comprador (papel customer); levanta EmailAlreadyUsed."""
        existing = await self.get_by_email(email)
        if existing is not None:
            raise EmailAlreadyUsed(email)
        user = User(
            email=email,
            password_hash=self.hasher.hash(password),
            full_name=full_name,
            role=UserRole.CUSTOMER,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Busca um usuário pelo e-mail (ou None)."""
        result = await self.session.scalars(select(User).where(User.email == email))
        return result.first()


class LoginAuditService:
    """Registra tentativas de login (sucesso e falha) para auditoria."""

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    async def record(
        self,
        email: str,
        success: bool,
        ip_address: str,
        user_id: int | None,
    ) -> None:
        """Persiste a tentativa de login; não levanta exceções."""
        attempt = LoginAttempt(
            email=email,
            success=success,
            ip_address=ip_address,
            user_id=user_id,
        )
        self.session.add(attempt)
        await self.session.flush()


class LoginAuditReader:
    """Lê registros de login_attempt para a área administrativa."""

    _PAGE_SIZE_MAX = 100

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    async def list_attempts(
        self,
        page: int,
        page_size: int,
        only_failures: bool,
    ) -> list[LoginAttempt]:
        """Retorna página de tentativas de login (mais recentes primeiro)."""
        effective_size = min(page_size, self._PAGE_SIZE_MAX)
        stmt = select(LoginAttempt)
        if only_failures:
            stmt = stmt.where(LoginAttempt.success.is_(False))
        stmt = stmt.order_by(LoginAttempt.id.desc())
        stmt = stmt.offset((page - 1) * effective_size).limit(effective_size)
        result = await self.session.scalars(stmt)
        return list(result.all())


class CustomerAdminReader:
    """Pesquisa e lista clientes para suporte administrativo."""

    _PAGE_SIZE_MAX = 100

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    async def search(
        self,
        query: str | None,
        page: int,
        page_size: int,
    ) -> list[User]:
        """Busca usuários por e-mail ou nome (parcial, case-insensitive).

        Sem filtro retorna todos os usuários paginados (mais recentes primeiro).
        Exclui contas anonimizadas (deleted_at preenchido).
        """
        effective_size = min(page_size, self._PAGE_SIZE_MAX)
        stmt = select(User).where(User.deleted_at.is_(None))
        if query:
            pattern = f"%{query.lower()}%"
            from sqlalchemy import func, or_
            stmt = stmt.where(
                or_(
                    func.lower(User.email).like(pattern),
                    func.lower(User.full_name).like(pattern),
                )
            )
        stmt = stmt.order_by(User.id.desc())
        stmt = stmt.offset((page - 1) * effective_size).limit(effective_size)
        result = await self.session.scalars(stmt)
        return list(result.all())


class WrongCurrentPassword(Exception):
    """Levantada quando a senha atual informada não confere."""


class PasswordChanger:
    """Altera a senha do usuário autenticado após validar a senha atual."""

    def __init__(self, session: AsyncSession, hasher: PasswordHasher) -> None:
        """Recebe a sessão e o hasher de senha por injeção."""
        self.session = session
        self.hasher = hasher

    async def change(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        """Valida a senha atual e aplica a nova.

        Levanta WrongCurrentPassword se a senha atual não conferir.
        """
        if not self.hasher.verify(current_password, user.password_hash):
            raise WrongCurrentPassword("Senha atual incorreta")
        user.password_hash = self.hasher.hash(new_password)
        await self.session.flush()


class UserNotFound(Exception):
    """Levantada quando o e-mail não existe no sistema (redefinição de senha)."""


class PasswordResetter:
    """Gerencia o fluxo de redefinição de senha (forgot/reset) usando JWT."""

    def __init__(
        self,
        session: AsyncSession,
        jwt: JwtService,
        hasher: PasswordHasher,
    ) -> None:
        """Recebe a sessão, serviço JWT e hasher por injeção."""
        self.session = session
        self.jwt = jwt
        self.hasher = hasher

    async def request_reset(self, email: str) -> str:
        """Gera e retorna o token JWT de redefinição.

        Retorna o token mesmo se o e-mail não existir (evita enumeração).
        Levanta UserNotFound apenas se a aplicação precisar enviar o e-mail.
        """
        result = await self.session.scalars(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        user = result.first()
        if user is None:
            raise UserNotFound(email)
        return self.jwt.issue_reset(email)

    async def reset_password(self, token: str, new_password: str) -> None:
        """Valida o token e aplica a nova senha.

        Levanta InvalidToken se o token for inválido ou expirado.
        Levanta UserNotFound se o e-mail não existir.
        """
        from app.security.jwt import InvalidToken

        try:
            email = self.jwt.verify_reset(token)
        except InvalidToken:
            raise
        result = await self.session.scalars(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        user = result.first()
        if user is None:
            raise UserNotFound(email)
        user.password_hash = self.hasher.hash(new_password)
        await self.session.flush()


class AccountDeletionService:
    """Anonimiza e desativa a conta conforme requisito LGPD (Art. 18 LGPD).

    A conta não é removida fisicamente para manter integridade referencial;
    o e-mail é substituído por hash SHA-256 e dados pessoais são apagados.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão por injeção."""
        self.session = session

    async def delete_account(self, user: User) -> None:
        """Anonimiza a conta: marca deleted_at, substitui dados pessoais por hash."""
        email_hash = hashlib.sha256(user.email.encode()).hexdigest()
        user.email = f"deleted-{email_hash}@anonymized.invalid"
        user.full_name = "Conta removida"
        user.password_hash = ""
        user.is_active = False
        user.deleted_at = datetime.now(UTC)
        await self.session.flush()
