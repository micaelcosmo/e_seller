"""Handlers globais: mapeiam exceções de domínio para respostas HTTP coerentes."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.accounts.services import EmailAlreadyUsed, InvalidCredentials
from app.billing.services import InvalidDocument
from app.cart.services import AlreadyOwned, CartProductNotFound
from app.catalog.asset_service import ProductAssetNotFound
from app.catalog.services import (
    InvalidManifestUrl,
    InvalidStatus,
    ManifestError,
    ProductNotFound,
)
from app.coupons.services import CouponInvalid
from app.delivery.services import DownloadLimitReached, GrantExpired, GrantNotFound
from app.orders.services import OrderNotFound
from app.orders.state_machine import InvalidTransition
from app.refunds.services import PaymentNotFound, RefundNotAllowed
from app.reviews.services import AlreadyReviewed, InvalidRating, ReviewNotAllowed
from app.security.storage import FileMissing
from app.wishlist.services import WishlistProductNotFound

_STATUS_TITLES: dict[int, str] = {
    400: "Requisição inválida",
    401: "Não autenticado",
    403: "Sem permissão",
    404: "Não encontrado",
    409: "Conflito de estado",
    410: "Recurso expirado",
    422: "Dados inválidos",
    429: "Limite atingido",
    500: "Erro interno",
}


def _json_error(status: int, detail: str, instance: str = "/") -> JSONResponse:
    """Monta uma JSONResponse Problem+JSON (RFC 9457) padronizada."""
    body = {
        "type": f"https://e-seller.app/errors/{status}",
        "title": _STATUS_TITLES.get(status, "Erro"),
        "status": status,
        "detail": detail,
        "instance": instance,
    }
    return JSONResponse(
        status_code=status,
        content=body,
        media_type="application/problem+json",
    )


class DomainHandlers:
    """Registra handlers de exceções de domínio na aplicação FastAPI.

    Cada exceção de domínio é mapeada para um código HTTP e mensagem canônicos,
    evitando try/except repetitivos nos routers.
    """

    # Mapeamento: tipo de exceção → (código HTTP, mensagem).
    _MAP: dict[type[Exception], tuple[int, str]] = {
        # 404 — Não encontrado
        ProductNotFound: (404, "Produto não encontrado"),
        ProductAssetNotFound: (404, "Produto não encontrado"),
        CartProductNotFound: (404, "Produto não encontrado"),
        WishlistProductNotFound: (404, "Produto não encontrado"),
        OrderNotFound: (404, "Pedido não encontrado"),
        GrantNotFound: (404, "Link de download inválido"),
        FileMissing: (404, "Arquivo indisponível"),
        # 409 — Conflito de estado
        AlreadyReviewed: (409, "Você já avaliou este e-book"),
        AlreadyOwned: (409, "Você já possui este e-book"),
        PaymentNotFound: (409, "Pedido sem pagamento aprovado"),
        InvalidTransition: (409, "Pedido não está em estado estornável"),
        EmailAlreadyUsed: (409, "E-mail já cadastrado"),
        # 410 — Recurso expirado
        GrantExpired: (410, "Link de download expirado"),
        # 422 — Dados inválidos
        InvalidManifestUrl: (422, "URL inválida"),
        ManifestError: (422, "Manifest inválido"),
        InvalidStatus: (422, "Status inválido (use published ou draft)"),
        CouponInvalid: (422, "Cupom inválido"),
        InvalidRating: (422, "Nota inválida (1 a 5)"),
        InvalidDocument: (422, "Documento fiscal inválido"),
        RefundNotAllowed: (422, "Valor de estorno inválido"),
        # 403 — Sem permissão de negócio
        ReviewNotAllowed: (403, "Só quem comprou pode avaliar"),
        # 429 — Limite atingido
        DownloadLimitReached: (429, "Limite de downloads atingido"),
        # 401 — Não autenticado
        InvalidCredentials: (401, "Credenciais inválidas"),
    }

    @classmethod
    def register(cls, app: FastAPI) -> None:
        """Registra todos os handlers na instância da aplicação."""
        for exc_class, (status, detail) in cls._MAP.items():
            app.add_exception_handler(exc_class, cls._make_handler(status, detail))

    @staticmethod
    def _make_handler(status: int, detail: str):
        """Cria um handler assíncrono para retornar a resposta Problem+JSON."""

        async def handler(request: Request, exc: Exception) -> JSONResponse:
            """Converte a exceção de domínio em Problem+JSON (RFC 9457)."""
            return _json_error(status, detail, instance=str(request.url.path))

        return handler
