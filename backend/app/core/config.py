"""Configuração da aplicação, carregada de variáveis de ambiente."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Valores de configuração lidos do ambiente (ou de um arquivo .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    app_version: str = "0.1.0"
    app_secret_key: str = "dev-secret-change-me"
    # Driver async por padrão: sqlite+aiosqlite (dev/test) ou postgresql+asyncpg (prod).
    database_url: str = "sqlite+aiosqlite:///./e_seller.db"
    storage_dir: str = "storage/ebooks"
    base_url: str = "http://localhost:48080"
    payment_provider: str = "fake"
    download_ttl_days: int = 7
    download_max: int = 5
    # Autenticação (sobrescrever por env em produção).
    jwt_ttl_seconds: int = 3600
    # Refresh token com validade maior (padrão: 7 dias = 604 800 s).
    jwt_refresh_ttl_seconds: int = 604_800
    # Custo do PBKDF2 (iterações): tunável por ambiente conforme o hardware.
    password_hash_iterations: int = 200_000
    admin_email: str = "admin@e_seller.local"
    admin_password: str = "change-me-dev"
    # Segredo do webhook Mercado Pago (usado quando payment_provider=mercadopago).
    mercadopago_webhook_secret: str = ""
    # CORS: origens permitidas separadas por vírgula (vazio = "*" apenas em dev).
    cors_origins: str = ""
    # Logging: nível configurável por ambiente (DEBUG/INFO/WARNING/ERROR).
    log_level: str = "INFO"
    # SMTP para e-mails transacionais (vazio = desabilitado).
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@e_seller.local"
    # Content-Security-Policy enviado em todas as respostas HTTP.
    csp_header: str = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'"
    )
    # HSTS (Strict-Transport-Security): max-age em segundos.
    # 0 = desativado (dev/http); 31536000 = 1 ano (produção HTTPS).
    hsts_max_age: int = 0
    # Ativa echo de queries SQL (apenas dev — nunca em produção).
    db_echo: bool = False
    # Limiar (ms) para logar queries lentas (0 = desativado).
    db_slow_query_ms: int = 0
    # 2FA/TOTP: chave AES-256-GCM em base64 (32 bytes) para cifrar secrets TOTP.
    # Gerar: python -c "import base64,secrets; print(base64.b64encode(secrets.token_bytes(32)).decode())"  # noqa: E501
    totp_encryption_key: str = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    # Papéis que exigem 2FA ativo para fazer login completo.
    two_fa_required_roles: list[str] = ["admin", "staff"]
    # DB Connection pool (async SQLAlchemy).
    db_pool_size: int = 10
    db_pool_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_pre_ping: bool = True


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância única (cacheada) de Settings."""
    return Settings()
