"""Regressão QAF-03: o download compara validade com data que vem COM fuso (Postgres).

Spec: `.spec/enrichment/roadmap-qaf.md` (QAF-03). `download_grant.expires_at` é
`timestamptz`: o Postgres devolve datetime com fuso, e `Clock.now()` é UTC sem
fuso — comparar os dois levanta TypeError e todo download respondia 500. Em
SQLite o valor volta sem fuso, então o teste monta o grant como o Postgres devolve.
"""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.core.clock import Clock
from app.delivery.services import DownloadLimitReached, GrantExpired, GrantValidator


class _RelogioFixo(Clock):
    """Relógio parado num instante conhecido (UTC, sem fuso, como o de produção)."""

    def __init__(self, instante: datetime) -> None:
        """Guarda o instante devolvido por now()."""
        self.instante = instante

    def now(self) -> datetime:
        """O instante fixo."""
        return self.instante


class _GrantComFuso:
    """Grant como o Postgres devolve: `expires_at` com tzinfo."""

    def __init__(
        self, expires_at: datetime, download_count: int, max_downloads: int = 5
    ) -> None:
        """Campos usados pelo validador."""
        self.expires_at = expires_at
        self.download_count = download_count
        self.max_downloads = max_downloads


class _Resultado:
    """Resultado de `scalars()` com um único grant."""

    def __init__(self, grant) -> None:
        """Guarda o grant."""
        self.grant = grant

    def first(self):
        """O grant (ou None)."""
        return self.grant


class _SessaoFalsa:
    """Sessão que devolve o grant pedido e aceita flush."""

    def __init__(self, grant) -> None:
        """Guarda o grant."""
        self.grant = grant

    async def scalars(self, statement):
        """Qualquer SELECT devolve o grant."""
        return _Resultado(self.grant)

    async def flush(self) -> None:
        """Sem banco: nada a fazer."""
        return None


AGORA = datetime(2026, 9, 27, 12, 0, 0)


async def test_link_valido_com_fuso_e_consumido():
    """Validade futura com fuso: consome e incrementa o contador."""
    grant = _GrantComFuso(datetime(2026, 10, 4, 12, 0, tzinfo=UTC), 0)
    validador = GrantValidator(_SessaoFalsa(grant), _RelogioFixo(AGORA))
    consumido = await validador.consume("token")
    assert consumido.download_count == 1


async def test_link_vencido_com_fuso_e_expirado():
    """Validade passada com fuso: GrantExpired (410), não TypeError (500)."""
    grant = _GrantComFuso(datetime(2026, 9, 26, 12, 0, tzinfo=UTC), 0)
    validador = GrantValidator(_SessaoFalsa(grant), _RelogioFixo(AGORA))
    with pytest.raises(GrantExpired):
        await validador.consume("token")


async def test_link_esgotado_com_fuso_atinge_o_limite():
    """Validade futura com fuso e 5/5 downloads: DownloadLimitReached."""
    grant = _GrantComFuso(datetime(2026, 10, 4, 12, 0, tzinfo=UTC), 5)
    validador = GrantValidator(_SessaoFalsa(grant), _RelogioFixo(AGORA))
    with pytest.raises(DownloadLimitReached):
        await validador.consume("token")


def test_normalizar_converte_outro_fuso_para_utc_sem_fuso():
    """Data em -03:00 vira o mesmo instante em UTC, sem tzinfo."""
    menos_tres = datetime(2026, 9, 27, 6, 0, tzinfo=timezone(timedelta(hours=-3)))
    normalizado = Clock().as_naive_utc(menos_tres)
    assert normalizado == datetime(2026, 9, 27, 9, 0)
    assert normalizado.tzinfo is None
