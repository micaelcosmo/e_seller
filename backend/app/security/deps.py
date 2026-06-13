"""Dependencies de segurança: usuário atual (JWT/API Key) e autorização por papel."""

from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.security.blacklist import TokenBlacklistService
from app.security.jwt import InvalidToken, JwtService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


def get_jwt_service(settings: Settings = Depends(get_settings)) -> JwtService:
    """Constrói o serviço de JWT com a chave e os TTLs das settings."""
    return JwtService(
        settings.app_secret_key,
        ttl_seconds=settings.jwt_ttl_seconds,
        refresh_ttl_seconds=settings.jwt_refresh_ttl_seconds,
    )


async def _resolve_user_from_api_key(
    api_key: str, session: AsyncSession
) -> User | None:
    """Tenta autenticar via X-API-Key; retorna User ou None."""
    from app.accounts.services_aaa import ApiKeyService

    svc = ApiKeyService(session)
    return await svc.authenticate(api_key)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    jwt: JwtService = Depends(get_jwt_service),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Resolve o usuário autenticado via Bearer JWT ou X-API-Key; senão 401.

    Tenta JWT primeiro. Se ausente, tenta X-API-Key. Verifica blacklist no JWT.
    """
    if x_api_key and not token:
        user = await _resolve_user_from_api_key(x_api_key, session)
        if user is None:
            raise HTTPException(status_code=401, detail="API Key inválida")
        return user
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    try:
        claims = jwt.verify(token)
    except InvalidToken as error:
        raise HTTPException(status_code=401, detail="Token inválido") from error
    jti = claims.get("jti")
    if jti:
        blacklist = TokenBlacklistService(session)
        if await blacklist.is_revoked(jti):
            raise HTTPException(status_code=401, detail="Token revogado")
    result = await session.scalars(select(User).where(User.email == claims.get("sub")))
    user = result.first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuário inválido")
    return user


async def get_optional_user(
    token: str | None = Depends(oauth2_scheme),
    jwt: JwtService = Depends(get_jwt_service),
    session: AsyncSession = Depends(get_session),
) -> User | None:
    """Resolve o usuário se houver token válido; senão retorna None (sem erro)."""
    if not token:
        return None
    try:
        claims = jwt.verify(token)
    except InvalidToken:
        return None
    jti = claims.get("jti")
    if jti:
        blacklist = TokenBlacklistService(session)
        if await blacklist.is_revoked(jti):
            return None
    result = await session.scalars(select(User).where(User.email == claims.get("sub")))
    user = result.first()
    if user is None or not user.is_active:
        return None
    return user


class RequireRole:
    """Dependency chamável que autoriza o acesso por papel (RBAC)."""

    def __init__(self, *allowed: str) -> None:
        """Recebe os papéis permitidos."""
        self.allowed = allowed

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        """Permite o acesso se o usuário tiver um papel permitido; senão 403."""
        permitted = False
        for role in self.allowed:
            if user.role.value == role:
                permitted = True
        if not permitted:
            raise HTTPException(status_code=403, detail="Sem permissão")
        return user
