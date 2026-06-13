"""Fábrica da aplicação FastAPI do e_seller (async)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Importa os módulos de models para registrá-los na metadata antes do create_all.
from app.accounts import models as _accounts_models  # noqa: F401
from app.accounts.router import router as accounts_router
from app.accounts.router_admin import router as accounts_admin_router
from app.admin.audit import AdminAuditLog as _AdminAuditLog  # noqa: F401
from app.admin.auth import AdminAuth
from app.admin.router_audit import router as audit_log_router
from app.admin.setup import setup_admin
from app.billing import models as _billing_models  # noqa: F401
from app.billing.router import router as billing_router
from app.cart import models as _cart_models  # noqa: F401
from app.cart.router import router as cart_router
from app.catalog import models as _catalog_models  # noqa: F401
from app.catalog.router import router as catalog_router
from app.catalog.router_admin import router as catalog_admin_router
from app.core.config import Settings, get_settings
from app.core.csrf import CSRFMiddleware
from app.core.db import Database
from app.core.email import EmailFailCounter
from app.core.exception_handlers import DomainHandlers
from app.core.logging_config import LoggingConfig
from app.core.middleware import (
    CorrelationIdMiddleware,
    ProcessTimeMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.rate_limit import LoginFailTracker, _InMemoryStore
from app.core.router_alerts import router as alerts_router
from app.core.router_dashboard import router as dashboard_router
from app.core.router_health import root_router as health_root_router
from app.core.router_health import router as health_router
from app.core.router_metrics import router as metrics_router
from app.core.schema_sync import SchemaSync
from app.coupons import models as _coupons_models  # noqa: F401
from app.coupons.router import router as coupons_router
from app.coupons.router_admin import router as coupons_admin_router
from app.delivery import models as _delivery_models  # noqa: F401
from app.delivery.router import router as download_router
from app.delivery.router_admin import router as delivery_admin_router
from app.delivery.router_admin_downloads import router as downloads_admin_router
from app.entitlement import models as _entitlement_models  # noqa: F401
from app.entitlement.router import router as library_router
from app.newsletter import models as _newsletter_models  # noqa: F401
from app.newsletter.router import router as newsletter_router
from app.newsletter.router_admin import router as newsletter_admin_router
from app.orders import models as _orders_models  # noqa: F401
from app.orders.router import router as orders_router
from app.orders.router_admin_html import router as orders_admin_panel_router
from app.orders.router_reports import router as reports_router
from app.payments import models as _payments_models  # noqa: F401
from app.payments.router import router as webhook_router
from app.refunds import models as _refunds_models  # noqa: F401
from app.refunds.router import router as refunds_router
from app.reviews import models as _reviews_models  # noqa: F401
from app.reviews.router import router as reviews_router
from app.reviews.router_admin import router as reviews_admin_router
from app.security.jwt import JwtService
from app.security.passwords import PasswordHasher
from app.security.storage import ProtectedStorage
from app.seeds import DevSeeder
from app.web.router import router as web_router
from app.wishlist import models as _wishlist_models  # noqa: F401
from app.wishlist.router import router as wishlist_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Ciclo de vida: cria as tabelas e semeia dados de dev na inicialização."""
    database: Database = app.state.database
    settings: Settings = app.state.settings
    await database.create_all()
    await SchemaSync(database.engine).run()
    if settings.app_env == "dev":
        await _seed_dev_data(database, settings)
    yield


async def _seed_dev_data(database: Database, settings: Settings) -> None:
    """Semeia produtos de exemplo e o usuário admin (idempotente)."""
    session = database.create_session()
    try:
        storage = ProtectedStorage(settings.storage_dir)
        seeder = DevSeeder(session, storage)
        await seeder.run()
        await seeder.ensure_admin(
            settings.admin_email,
            settings.admin_password,
            PasswordHasher(settings.password_hash_iterations),
        )
        await seeder.ensure_coupon()
    finally:
        await session.close()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Cria e configura a aplicação FastAPI (rotas, banco async, CORS, lifespan)."""
    active_settings = settings or get_settings()
    # Logging JSON + correlation ID na inicialização (antes de qualquer requisição).
    LoggingConfig(level=active_settings.log_level).setup()
    app = FastAPI(title="e_seller API", version="0.2.0", lifespan=lifespan)
    app.state.database = Database(
        active_settings.database_url,
        echo=active_settings.db_echo,
        slow_query_ms=active_settings.db_slow_query_ms,
    )
    app.state.settings = active_settings
    app.state.rate_store = _InMemoryStore()
    app.state.email_fail_counter = EmailFailCounter()
    app.state.login_fail_tracker = LoginFailTracker(max_failures=5, window_seconds=300)
    import time as _time
    app.state.started_at = _time.monotonic()

    DomainHandlers.register(app)

    # CSRF: token em cookie para formulários HTML; rotas /api/ são isentas.
    app.add_middleware(CSRFMiddleware)
    # Gzip: comprime respostas >= 1000 bytes (reduz tráfego para clientes que aceitam).
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    # Security headers (CSP, X-Frame-Options etc.) — mais externo para cobrir tudo.
    app.add_middleware(SecurityHeadersMiddleware)
    # Process time em todas as respostas (latência para monitoramento).
    app.add_middleware(ProcessTimeMiddleware)
    # Correlation ID antes do CORS para que todas as respostas carreguem o header.
    app.add_middleware(CorrelationIdMiddleware)
    # CORS: produção define CORS_ORIGINS (vírgula-separada); dev aceita qualquer origem.
    if active_settings.cors_origins:
        allowed_origins = []
        for origin in active_settings.cors_origins.split(","):
            origin = origin.strip()
            if origin:
                allowed_origins.append(origin)
    else:
        allowed_origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_root_router)
    app.include_router(health_router)
    app.include_router(metrics_router)
    app.include_router(dashboard_router)
    app.include_router(alerts_router)
    app.include_router(accounts_router)
    app.include_router(accounts_admin_router)
    app.include_router(catalog_router)
    app.include_router(catalog_admin_router)
    app.include_router(coupons_router)
    app.include_router(coupons_admin_router)
    app.include_router(cart_router)
    app.include_router(orders_router)
    app.include_router(orders_admin_panel_router)
    app.include_router(reports_router)
    app.include_router(webhook_router)
    app.include_router(download_router)
    app.include_router(delivery_admin_router)
    app.include_router(downloads_admin_router)
    app.include_router(library_router)
    app.include_router(reviews_router)
    app.include_router(reviews_admin_router)
    app.include_router(wishlist_router)
    app.include_router(newsletter_router)
    app.include_router(newsletter_admin_router)
    app.include_router(audit_log_router)
    app.include_router(billing_router)
    app.include_router(refunds_router)
    app.include_router(web_router)

    _static_dir = Path(__file__).parent / "web" / "static"
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

    _tmpl_dir = str(Path(__file__).parent / "web" / "templates")
    _templates = Jinja2Templates(directory=_tmpl_dir)

    async def _handle_404(request: Request, exc: Exception) -> HTMLResponse:
        """Renderiza 404 HTML para browser ou JSON para /api/."""
        if request.url.path.startswith("/api/"):
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=404, content={"detail": "Não encontrado"})
        html = _templates.get_template("custom_404.html").render({"request": request})
        return HTMLResponse(html, status_code=404)

    async def _handle_500(request: Request, exc: Exception) -> HTMLResponse:
        """Renderiza 500 HTML para browser ou JSON para /api/."""
        if request.url.path.startswith("/api/"):
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=500, content={"detail": "Erro interno"})
        html = _templates.get_template("custom_500.html").render({"request": request})
        return HTMLResponse(html, status_code=500)

    app.add_exception_handler(404, _handle_404)  # type: ignore[arg-type]
    app.add_exception_handler(500, _handle_500)  # type: ignore[arg-type]

    # Painel administrativo (SQLAdmin) protegido por login de staff/admin.
    admin_jwt = JwtService(
        active_settings.app_secret_key, ttl_seconds=active_settings.jwt_ttl_seconds
    )
    auth_backend = AdminAuth(
        active_settings.app_secret_key,
        app.state.database,
        admin_jwt,
        active_settings.password_hash_iterations,
    )
    setup_admin(app, app.state.database.engine, auth_backend)
    return app


# Instância padrão usada pelo Uvicorn (uvicorn app.main:app).
app = create_app()
