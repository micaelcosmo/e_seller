"""Backend de autenticação do painel SQLAdmin (acesso só para staff/admin)."""

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.accounts.services import Authenticator
from app.core.db import Database
from app.security.jwt import InvalidToken, JwtService
from app.security.passwords import PasswordHasher

_STAFF_ROLES = ("admin", "staff")


class AdminAuth(AuthenticationBackend):
    """Valida login do painel via conta de banco e protege as rotas do admin."""

    def __init__(
        self,
        secret_key: str,
        database: Database,
        jwt: JwtService,
        hash_iterations: int = 200_000,
    ) -> None:
        """Recebe a chave de sessão, o banco, o JWT e o custo do hash de senha."""
        super().__init__(secret_key=secret_key)
        self.database = database
        self.jwt = jwt
        self.hasher = PasswordHasher(hash_iterations)

    async def login(self, request: Request) -> bool:
        """Autentica o operador; só permite papéis staff/admin."""
        form = await request.form()
        email = str(form.get("username", ""))
        password = str(form.get("password", ""))
        session = self.database.create_session()
        try:
            user = await Authenticator(
                session, self.hasher, self.jwt
            ).get_by_email(email)
        finally:
            await session.close()
        if user is None or not user.is_active or user.role.value not in _STAFF_ROLES:
            return False
        if not self.hasher.verify(password, user.password_hash):
            return False
        request.session["token"] = self.jwt.issue(subject=user.email)
        return True

    async def logout(self, request: Request) -> bool:
        """Encerra a sessão do painel."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Verifica se a sessão do painel tem um token válido."""
        token = request.session.get("token")
        if not token:
            return False
        try:
            self.jwt.verify(token)
        except InvalidToken:
            return False
        return True
