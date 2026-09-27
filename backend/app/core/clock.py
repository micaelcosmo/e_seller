"""Relógio injetável, para tornar o tempo testável (sem usar o relógio real direto)."""

from datetime import UTC, datetime


class Clock:
    """Fornece o instante atual em UTC (naive), permitindo substituição em testes."""

    def now(self) -> datetime:
        """Retorna o agora em UTC, sem tzinfo (compatível com o banco)."""
        return datetime.now(UTC).replace(tzinfo=None)

    def as_naive_utc(self, moment: datetime) -> datetime:
        """Converte um instante para UTC sem tzinfo, a mesma base de `now()`.

        Colunas `timestamptz` voltam com fuso no Postgres e sem fuso no SQLite;
        comparar com `now()` exige normalizar antes.
        """
        if moment.tzinfo is None:
            return moment
        return moment.astimezone(UTC).replace(tzinfo=None)
