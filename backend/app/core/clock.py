"""Relógio injetável, para tornar o tempo testável (sem usar o relógio real direto)."""

from datetime import UTC, datetime


class Clock:
    """Fornece o instante atual em UTC (naive), permitindo substituição em testes."""

    def now(self) -> datetime:
        """Retorna o agora em UTC, sem tzinfo (compatível com o banco)."""
        return datetime.now(UTC).replace(tzinfo=None)
