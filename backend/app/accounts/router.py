"""Rotas de autenticação e contas (login, registro, perfil, AAA)."""

from __future__ import annotations

import re
from datetime import UTC, datetime

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
from app.accounts.services_aaa import (
    ApiKeyService,
    TOTPService,
    UserActivityLogService,
)
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.core.email import EmailService
from app.core.rate_limit import AuthAwareRateLimit, LoginFailTracker, RateLimit
from app.security.blacklist import TokenBlacklistService
from app.security.deps import get_current_user, get_jwt_service, oauth2_scheme
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


class PartialTokenOut(BaseModel):
    """Resposta do login quando 2FA está ativado: token parcial."""

    partial_token: str
    requires_2fa: bool = True


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


@router.post("/token")
async def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    auth: Authenticator = Depends(get_authenticator),
    jwt: JwtService = Depends(get_jwt_service),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
    _limit: None = Depends(_login_limit),
) -> TokenOut | PartialTokenOut:
    """Autentica (OAuth2 password); retorna tokens ou partial_token se 2FA ativo.

    Quando o usuário tem 2FA ativado e seu papel está em two_fa_required_roles,
    retorna {partial_token, requires_2fa: true}. O cliente deve chamar POST /2fa/login.
    Registra a tentativa (sucesso ou falha) na tabela login_attempt usando
    uma sessão independente, para que falhas de autenticação não sejam revertidas.
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
    authenticated_user: User | None = None
    try:
        try:
            access_token = await auth.login(form.username, form.password)
            success = True
            authenticated_user = await auth.get_by_email(form.username)
            user_id = authenticated_user.id if authenticated_user is not None else None
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
    if authenticated_user is None:
        authenticated_user = await auth.get_by_email(form.username)
    requires_two_fa = (
        authenticated_user is not None
        and authenticated_user.totp_enabled
        and authenticated_user.role.value in settings.two_fa_required_roles
    )
    if requires_two_fa:
        partial = jwt._issue_partial(form.username)
        return PartialTokenOut(partial_token=partial)
    activity_svc = UserActivityLogService(session)
    await activity_svc.log("login", user_id=user_id, ip=ip)
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


# ──────────────────────────────────────────────────────────────────────────────
# AAA — Logout / Blacklist
# ──────────────────────────────────────────────────────────────────────────────


@router.post("/logout", status_code=204, tags=["auth"])
async def logout(
    token: str | None = Depends(oauth2_scheme),
    jwt: JwtService = Depends(get_jwt_service),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Revoga o access token atual (jti na blacklist). Retorna 204.

    Tokens sem claim jti (emitidos antes do enrichment) são ignorados silenciosamente.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    try:
        claims = jwt.verify(token)
    except InvalidToken as exc:
        raise HTTPException(status_code=401, detail="Token inválido") from exc
    jti = claims.get("jti")
    if jti:
        exp = claims.get("exp", 0)
        expires_at = datetime.fromtimestamp(exp, tz=UTC)
        blacklist = TokenBlacklistService(session)
        await blacklist.revoke(jti, expires_at)


# ──────────────────────────────────────────────────────────────────────────────
# AAA — User Activity Log
# ──────────────────────────────────────────────────────────────────────────────


class ActivityLogOut(BaseModel):
    """Registro de atividade do usuário."""

    id: int
    event_type: str
    meta: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/me/activity", response_model=list[ActivityLogOut], tags=["accounts"])
async def my_activity(
    skip: int = 0,
    limit: int = 20,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ActivityLogOut]:
    """Lista as atividades recentes do usuário autenticado (paginadas)."""
    service = UserActivityLogService(session)
    entries = await service.list_for_user(user.id, skip=skip, limit=limit)
    return [ActivityLogOut.model_validate(e) for e in entries]


# ──────────────────────────────────────────────────────────────────────────────
# AAA — API Keys
# ──────────────────────────────────────────────────────────────────────────────


class ApiKeyCreateIn(BaseModel):
    """Dados para criar uma nova API Key."""

    name: str
    expires_at: datetime | None = None


class ApiKeyOut(BaseModel):
    """Resposta de listagem de API Keys (sem expor o hash)."""

    id: int
    name: str
    prefix: str
    is_active: bool
    last_used_at: datetime | None
    expires_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreatedOut(ApiKeyOut):
    """Resposta de criação: inclui a chave crua (exibida UMA ÚNICA VEZ)."""

    key: str


@router.get("/me/api-keys", response_model=list[ApiKeyOut], tags=["accounts"])
async def list_api_keys(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ApiKeyOut]:
    """Lista as API Keys ativas do usuário autenticado."""
    service = ApiKeyService(session)
    keys = await service.list_keys(user.id)
    return [ApiKeyOut.model_validate(k) for k in keys]


@router.post(  # noqa: E501
    "/me/api-keys", response_model=ApiKeyCreatedOut, status_code=201, tags=["accounts"]
)
async def create_api_key(
    data: ApiKeyCreateIn,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiKeyCreatedOut:
    """Cria uma nova API Key; a chave crua é retornada UMA ÚNICA VEZ."""
    service = ApiKeyService(session)
    raw, key = await service.generate(user.id, data.name, data.expires_at)
    out = ApiKeyOut.model_validate(key)
    return ApiKeyCreatedOut(**out.model_dump(), key=raw)


@router.delete("/me/api-keys/{key_id}", status_code=204, tags=["accounts"])
async def revoke_api_key(
    key_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Revoga (desativa) uma API Key do usuário autenticado."""
    service = ApiKeyService(session)
    found = await service.revoke(key_id, user.id)
    if not found:
        raise HTTPException(status_code=404, detail="API Key não encontrada.")


# ──────────────────────────────────────────────────────────────────────────────
# AAA — TOTP 2FA
# ──────────────────────────────────────────────────────────────────────────────


class TotpEnrollOut(BaseModel):
    """Resposta do enrollment 2FA: URI provisioning e secret."""

    secret: str
    provisioning_uri: str


class TotpConfirmIn(BaseModel):
    """Confirma enrollment com código TOTP gerado pelo app autenticador."""

    secret: str
    code: str


class TotpDisableIn(BaseModel):
    """Desativa 2FA exigindo senha atual + código TOTP."""

    password: str
    code: str


class TotpLoginIn(BaseModel):
    """Passo 2 do login: partial_token + código TOTP."""

    partial_token: str
    code: str


def _get_totp_service(settings: Settings = Depends(get_settings)) -> TOTPService:
    """Constrói o TOTPService com a chave de cifração das settings."""
    return TOTPService(settings.totp_encryption_key)


@router.post("/2fa/enroll", response_model=TotpEnrollOut, tags=["auth"])
async def totp_enroll(
    user: User = Depends(get_current_user),
    totp_svc: TOTPService = Depends(_get_totp_service),
) -> TotpEnrollOut:
    """Inicia o enrollment 2FA: retorna secret e URI para QR Code.

    Não persiste ainda — confirmar com POST /2fa/confirm.
    """
    if user.totp_enabled:
        raise HTTPException(status_code=400, detail="2FA já está ativado.")
    secret = totp_svc.generate_secret()
    uri = totp_svc.generate_provisioning_uri(secret, user.email)
    return TotpEnrollOut(secret=secret, provisioning_uri=uri)


@router.post("/2fa/confirm", status_code=204, tags=["auth"])
async def totp_confirm(
    data: TotpConfirmIn,
    user: User = Depends(get_current_user),
    totp_svc: TOTPService = Depends(_get_totp_service),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Confirma o enrollment 2FA com o código gerado pelo app autenticador.

    Persiste o secret cifrado e ativa 2FA para o usuário.
    """
    if user.totp_enabled:
        raise HTTPException(status_code=400, detail="2FA já está ativado.")
    if not totp_svc.verify(data.secret, data.code):
        raise HTTPException(status_code=400, detail="Código TOTP inválido.")
    user.totp_secret_enc = totp_svc.encrypt_secret(data.secret)
    user.totp_enabled = True
    session.add(user)
    await session.commit()
    activity_svc = UserActivityLogService(session)
    await activity_svc.log("2fa_enrolled", user_id=user.id)


@router.post("/2fa/disable", status_code=204, tags=["auth"])
async def totp_disable(
    data: TotpDisableIn,
    user: User = Depends(get_current_user),
    totp_svc: TOTPService = Depends(_get_totp_service),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> None:
    """Desativa 2FA verificando senha atual e código TOTP correto."""
    if not user.totp_enabled:
        raise HTTPException(status_code=400, detail="2FA não está ativado.")
    hasher = PasswordHasher(settings.password_hash_iterations)
    if not hasher.verify(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Senha incorreta.")
    secret = totp_svc.decrypt_secret(user.totp_secret_enc)
    if not totp_svc.verify(secret, data.code):
        raise HTTPException(status_code=400, detail="Código TOTP inválido.")
    user.totp_secret_enc = None
    user.totp_enabled = False
    session.add(user)
    await session.commit()


@router.post("/2fa/login", response_model=TokenOut, tags=["auth"])
async def totp_login(
    data: TotpLoginIn,
    jwt: JwtService = Depends(get_jwt_service),
    totp_svc: TOTPService = Depends(_get_totp_service),
    session: AsyncSession = Depends(get_session),
) -> TokenOut:
    """Passo 2 do login com 2FA: valida partial_token + código TOTP.

    Retorna tokens completos (access + refresh) se o código for válido.
    """
    try:
        claims = jwt.verify(data.partial_token)
    except InvalidToken as exc:
        raise HTTPException(status_code=401, detail="Token parcial inválido.") from exc
    if claims.get("type") != "partial_2fa":
        raise HTTPException(status_code=401, detail="Token parcial inválido.")
    email = claims.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token parcial inválido.")
    result = await session.scalars(
        select(User).where(User.email == email, User.is_active.is_(True))
    )
    user = result.first()
    if user is None or not user.totp_enabled or not user.totp_secret_enc:
        raise HTTPException(status_code=401, detail="Usuário ou 2FA inválido.")
    secret = totp_svc.decrypt_secret(user.totp_secret_enc)
    if not totp_svc.verify(secret, data.code):
        raise HTTPException(status_code=400, detail="Código TOTP inválido.")
    access_token = jwt.issue(email)
    refresh_token = jwt.issue_refresh(email)
    return TokenOut(access_token=access_token, refresh_token=refresh_token)
