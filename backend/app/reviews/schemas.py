"""Schemas (Pydantic) de entrada/saída para avaliações de e-books."""

from __future__ import annotations

from pydantic import BaseModel


class ReviewIn(BaseModel):
    """Dados de entrada de uma avaliação (nota e comentário)."""

    rating: int
    comment: str = ""


class ReviewOut(BaseModel):
    """Representação de saída de uma avaliação (nota, texto, autor, data e id)."""

    id: int | None = None
    rating: int
    comment: str
    author: str
    created_at: str | None = None
