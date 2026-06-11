"""Rotas de autenticação e contas (login, registro, perfil)."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import User
from app.accounts.services import (
    AccountDeletionService,
    Authenticator,
    InvalidCredentials,
    LoginAuditService,
    PasswordChanger,
    PasswordResetter,
    UserNotFound,
    WrongCurrentPassword,
)
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.core.email import EmailService
from app.core.rate_limit import AuthAwareRateLimit, LoginFailTracker, RateLimit
from app.security.deps import get_current_user, get_jwt_service
from app.security.jwt import InvalidToken, JwtService
from app.security.passwords import PasswordHasher

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# 10 tentativas de login por minuto por IP — proteção contra brute-force.
_login_limit = RateLimit(max_requests=10, window_seconds=60)


class TokenOut(BaseModel):
    """Resposta do login: token de acesso e refresh token."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    """Entrada para renovar a sessão com o refresh token."""

    refresh_token: str


_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9.\-]+$")


class RegisterIn(BaseModel):
    """Dados de registro de um comprador."""

    email: str
    password: str
    full_name: str = ""

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Valida formato mínimo de e-mail (local@dominio.tld)."""
        if not _EMAIL_RE.match(value):
            raise ValueError("Formato de e-mail inválido.")
        return value.lower()


class MeOut(BaseModel):
    """Perfil do usuário autenticado."""

    email: str
    role: str
    full_name: str


def get_authenticator(
    session: AsyncSession = Depends(get_session),
    jwt: JwtService = Depends(get_jwt_service),
    settings: Settings = Depends(get_settings),
) -> Authenticator:
    """Monta o autenticador com hasher de senha e serviço de JWT."""
    hasher = PasswordHasher(settings.password_hash_iterations)
    return Authenticator(session, hasher, jwt)


@router.post("/token", response_model=TokenOut)
async def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    auth: Authenticator = Depends(get_authenticator),
    jwt: JwtService = Depends(get_jwt_service),
    session: AsyncSession = Depends(get_session),
    _limit: None = Depends(_login_limit),
) -> TokenOut:
    """Autentica (OAuth2 password) e retorna access + refresh token.

    Registra a tentativa (sucesso ou falha) na tabela login_attempt usando
    uma sessão independente, para que falhas de autenticação não sejam revertidas
    pelo rollback da sessão principal.
    """
    ip = request.client.host if request.client else ""
    database = request.app.state.database
    fail_tracker: LoginFailTracker = getattr(
        request.app.state, "login_fail_tracker", None
    )
    if fail_tracker is not None and fail_tracker.is_blocked(form.username):
        raise HTTPException(
            status_code=429,
            detail="Conta temporariamente bloqueada por excesso de tentativas.",
        )
    success = False
    user_id = None
    try:
        try:
            access_token = await auth.login(form.username, form.password)
            success = True
            user = await auth.get_by_email(form.username)
            user_id = user.id if user is not None else None
        except InvalidCredentials:
            if fail_tracker is not None:
                fail_tracker.record_failure(form.username)
            raise
    finally:
        audit_session = database.create_session()
        try:
            audit = LoginAuditService(audit_session)
            await audit.record(form.username, success, ip, user_id)
            await audit_session.commit()
        except Exception:
            await audit_session.rollback()
        finally:
            await audit_session.close()
    refresh_token = jwt.issue_refresh(form.username)
    return TokenOut(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenOut)
async def refresh(
    data: RefreshIn,
    jwt: JwtService = Depends(get_jwt_service),
    session: AsyncSession = Depends(get_session),
    _limit: None = Depends(_login_limit),
) -> TokenOut:
    """Renova a sessão usando um refresh token válido; retorna novos tokens.

    Retorna 401 se o refresh token for inválido ou expirado.
    """
    try:
        email = jwt.verify_refresh(data.refresh_token)
    except InvalidToken as error:
        raise HTTPException(status_code=401, detail="Refresh token inválido") from error
    result = await session.scalars(select(User).where(User.email == email))
    user = result.first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuário inválido")
    access_token = jwt.issue(email)
    new_refresh = jwt.issue_refresh(email)
    return TokenOut(access_token=access_token, refresh_token=new_refresh)


_limit_register = AuthAwareRateLimit(max_requests=5, window_seconds=60)


@router.post("/register", response_model=MeOut, status_code=201)
async def register(
    data: RegisterIn,
    auth: Authenticator = Depends(get_authenticator),
    _: None = Depends(_limit_register),
) -> MeOut:
    """Registra um comprador (conta opcional para comprar/navegar melhor).

    Levanta EmailAlreadyUsed (409) via handler global de exceções de domínio.
    """
    user = await auth.register_customer(data.email, data.password, data.full_name)
    return MeOut(email=user.email, role=user.role.value, full_name=user.full_name)


@router.get("/me", response_model=MeOut)
async def me(user: User = Depends(get_current_user)) -> MeOut:
    """Retorna o perfil do usuário autenticado."""
    return MeOut(email=user.email, role=user.role.value, full_name=user.full_name)


class ChangePasswordIn(BaseModel):
    """Dados de entrada para alterar a senha do usuário."""

    current_password: str
    new_password: str


@router.patch("/change-password", status_code=204)
async def change_password(
    data: ChangePasswordIn,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> None:
    """Altera a senha do usuário autenticado após validar a senha atual.

    Retorna 422 se a senha atual não conferir.
    """
    hasher = PasswordHasher(settings.password_hash_iterations)
    changer = PasswordChanger(session, hasher)
    try:
        await changer.change(user, data.current_password, data.new_password)
    except WrongCurrentPassword as exc:
        raise HTTPException(status_code=422, detail="Senha atual incorreta.") from exc


class ForgotPasswordIn(BaseModel):
    """Dados de entrada para solicitar a redefinição de senha."""

    email: str


class ResetPasswordIn(BaseModel):
    """Dados de entrada para redefinir a senha com token."""

    token: str
    new_password: str


_limit_forgot = RateLimit(max_requests=3, window_seconds=60)


def get_password_resetter(
    session: AsyncSession = Depends(get_session),
    jwt: JwtService = Depends(get_jwt_service),
    settings: Settings = Depends(get_settings),
) -> PasswordResetter:
    """Monta o serviço de redefinição de senha."""
    hasher = PasswordHasher(settings.password_hash_iterations)
    return PasswordResetter(session, jwt, hasher)


@router.post("/forgot-password", status_code=200)
async def forgot_password(
    data: ForgotPasswordIn,
    resetter: PasswordResetter = Depends(get_password_resetter),
    settings: Settings = Depends(get_settings),
    _limit: None = Depends(_limit_forgot),
) -> dict:
    """Envia link de redefinição de senha ao e-mail informado.

    Retorna 200 mesmo se o e-mail não existir — evita enumeração de contas.
    """
    try:
        token = await resetter.request_reset(data.email)
    except UserNotFound:
        return {"detail": "Se o e-mail existir, você receberá o link em breve."}
    reset_link = f"{settings.base_url}/recuperar-senha?token={token}"
    email_service = EmailService(settings)
    email_service.send_password_reset(data.email, reset_link)
    return {"detail": "Se o e-mail existir, você receberá o link em breve."}


@router.post("/reset-password", status_code=204)
async def reset_password(
    data: ResetPasswordIn,
    resetter: PasswordResetter = Depends(get_password_resetter),
) -> None:
    """Aplica nova senha usando o token de redefinição.

    Retorna 400 se o token for inválido ou expirado.
    Retorna 404 se o e-mail não existir (token adulterado).
    """
    try:
        await resetter.reset_password(data.token, data.new_password)
    except InvalidToken as exc:
        raise HTTPException(
            status_code=400, detail="Token inválido ou expirado."
        ) from exc
    except UserNotFound as exc:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.") from exc


@router.delete("/account", status_code=204)
async def delete_account(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Anonimiza a conta do usuário autenticado (LGPD Art. 18).

    O e-mail é substituído por hash SHA-256; dados pessoais são removidos.
    A conta é desativada (deleted_at preenchido) mas não removida fisicamente.
    Retorna 204 No Content em caso de sucesso.
    """
    service = AccountDeletionService(session)
    await service.delete_account(user)
