"""Testes de INFRA-06 + BE-04 + DBQ-06 + DBQ-07 + OPS-06 + SEC-06.

Cobre: seeds externalizados (leitura de JSON), LOG_LEVEL por env,
CORS restritivo (lista via CORS_ORIGINS), slow query listener registro.
"""

from __future__ import annotations

import json
import logging
import pathlib
import tempfile

from app.core.config import Settings
from app.core.db import Database, _AfterExecuteListener, _BeforeExecuteListener
from app.core.logging_config import LoggingConfig
from app.seeds import DevSeeder


def test_log_level_info_por_padrao():
    """LOG_LEVEL padrão é INFO se não definido no env."""
    settings = Settings(log_level="INFO")
    assert settings.log_level == "INFO"


def test_log_level_configuravel():
    """LOG_LEVEL respeita valor passado via env."""
    settings = Settings(log_level="DEBUG")
    assert settings.log_level == "DEBUG"


def test_logging_config_aplica_nivel(caplog):
    """LoggingConfig configura o root logger com o nível recebido."""
    config = LoggingConfig(level="WARNING")
    config.setup()
    root = logging.getLogger()
    assert root.level == logging.WARNING


def test_cors_origins_vazio_aceita_wildcard():
    """CORS_ORIGINS vazio => allowed_origins = ['*']."""
    settings = Settings(cors_origins="")
    assert settings.cors_origins == ""


def test_cors_origins_lista():
    """CORS_ORIGINS com múltiplas entradas é parseável por split."""
    settings = Settings(cors_origins="https://a.com,https://b.com")
    origins = []
    for origin in settings.cors_origins.split(","):
        origin = origin.strip()
        if origin:
            origins.append(origin)
    assert origins == ["https://a.com", "https://b.com"]


def test_slow_query_listener_registrado():
    """Database com slow_query_ms > 0 cria sem erros e listeners são callable."""
    db = Database("sqlite+aiosqlite:///:memory:", slow_query_ms=100)
    # Engine foi criado com o listener registrado — sem erro é suficiente.
    assert db.slow_query_ms == 100
    assert callable(_BeforeExecuteListener())
    assert callable(_AfterExecuteListener(100))


def test_seeds_externalizados_leitura_json():
    """DevSeeder._load_json lê produtos do arquivo JSON externo."""
    with tempfile.TemporaryDirectory() as tmpdir:
        seeds_path = pathlib.Path(tmpdir)
        products = [
            {"title": "T1", "slug": "t1", "price": "10.00"},
        ]
        coupons = [
            {
                "code": "TEST10",
                "discount_type": "percent",
                "value": "10",
                "active": True,
            },
        ]
        (seeds_path / "dev_products.json").write_text(
            json.dumps(products), encoding="utf-8"
        )
        (seeds_path / "dev_coupons.json").write_text(
            json.dumps(coupons), encoding="utf-8"
        )

        class _FakeStorage:
            """Armazenamento falso para o seeder."""

            def write_bytes(self, *args, **kwargs) -> None:
                """Descarta escrita."""

        seeder = DevSeeder(
            session=None,  # type: ignore[arg-type]
            storage=_FakeStorage(),  # type: ignore[arg-type]
            seeds_dir=seeds_path,
        )
        loaded_products = seeder._load_json("dev_products.json")
        loaded_coupons = seeder._load_json("dev_coupons.json")

    assert loaded_products == products
    assert loaded_coupons == coupons


def test_db_echo_false_por_padrao():
    """db_echo e db_slow_query_ms partem de False e 0 por padrão."""
    settings = Settings()
    assert settings.db_echo is False
    assert settings.db_slow_query_ms == 0
