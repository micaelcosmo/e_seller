"""Fixtures de teste: aplicação async isolada (SQLite async) com dados semeados."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
from app.main import create_app
from app.security.storage import ProtectedStorage
from app.seeds import DevSeeder


@pytest.fixture
def settings(tmp_path) -> Settings:
    """Cria settings de teste apontando para SQLite async e storage temporários."""
    db_path = tmp_path / "test.db"
    storage_path = tmp_path / "storage"
    return Settings(
        app_env="test",
        database_url=f"sqlite+aiosqlite:///{db_path.as_posix()}",
        storage_dir=str(storage_path),
        base_url="http://test",
    )


@pytest_asyncio.fixture
async def app(settings: Settings):
    """Constrói a aplicação de teste, sobrescreve settings e semeia dados."""
    application = create_app(settings)

    def override_settings() -> Settings:
        """Retorna as settings de teste para as dependências."""
        return settings

    application.dependency_overrides[get_settings] = override_settings
    await application.state.database.create_all()
    session = application.state.database.create_session()
    try:
        await DevSeeder(session, ProtectedStorage(settings.storage_dir)).run()
    finally:
        await session.close()
    yield application
    # Descarta o engine para não vazar conexões entre os testes.
    await application.state.database.engine.dispose()


@pytest_asyncio.fixture
async def client(app):
    """Cliente HTTP async de teste sobre a aplicação (ASGI, sem rede)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


@pytest_asyncio.fixture
async def db_session(app):
    """Sessão async ligada ao mesmo banco de teste da aplicação."""
    session = app.state.database.create_session()
    try:
        yield session
    finally:
        await session.close()
