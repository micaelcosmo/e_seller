"""Vitrine demo (server-rendered) e simulador de pagamento (modo dev, async)."""

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.services import ProductCatalog, ProductNotFound
from app.core.clock import Clock
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.coupons.services import CouponService
from app.delivery.models import DownloadGrant
from app.orders.services import OrderCreator, OrderNotFound, OrderReader
from app.payments.gateways import FakePaymentGateway
from app.payments.router import get_webhook_processor
from app.payments.services import (
    CheckoutService,
    WebhookNotification,
    WebhookProcessor,
)
from app.reviews.services import ReviewService

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap(
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> PlainTextResponse:
    """Gera o sitemap.xml com URLs de produtos publicados (SEO).

    Inclui a home e cada produto publicado com <loc> baseada em base_url.
    """
    catalog = ProductCatalog(session)
    products = await catalog.list_published(limit=500)
    base = settings.base_url.rstrip("/")
    urls = [f"<url><loc>{base}/</loc></url>"]
    for product in products:
        urls.append(f"<url><loc>{base}/#/produto/{product.slug}</loc></url>")
    xml_body = "\n".join(urls)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{xml_body}\n"
        "</urlset>"
    )
    return PlainTextResponse(content=xml, media_type="application/xml")


@router.get("/privacidade", response_class=HTMLResponse)
async def privacy_policy(request: Request) -> HTMLResponse:
    """Política de privacidade (LGPD Art. 9) — texto estático."""
    return templates.TemplateResponse(request, "privacy.html", {})


@router.get("/termos", response_class=HTMLResponse)
async def terms_of_service(request: Request) -> HTMLResponse:
    """Termos de uso do serviço — texto estático."""
    return templates.TemplateResponse(request, "terms.html", {})


@router.get("/conta", response_class=HTMLResponse)
async def conta_page(request: Request) -> HTMLResponse:
    """Página de conta do usuário (login/registro/dashboard SPA)."""
    return templates.TemplateResponse(request, "conta.html", {})


@router.get("/biblioteca", response_class=HTMLResponse)
async def biblioteca_page(request: Request) -> HTMLResponse:
    """Biblioteca do usuário (entitlements/downloads)."""
    return templates.TemplateResponse(request, "biblioteca.html", {})


@router.get("/carrinho", response_class=HTMLResponse)
async def carrinho_page(request: Request) -> HTMLResponse:
    """Carrinho de compras do usuário."""
    return templates.TemplateResponse(request, "carrinho.html", {})


@router.get("/favoritos", response_class=HTMLResponse)
async def favoritos_page(request: Request) -> HTMLResponse:
    """Lista de favoritos (wishlist) do usuário."""
    return templates.TemplateResponse(request, "favoritos.html", {})


@router.get("/recuperar-senha", response_class=HTMLResponse)
async def password_recovery_page(request: Request) -> HTMLResponse:
    """Tela de recuperação/redefinição de senha.

    Sem token: exibe formulário de e-mail (esqueci minha senha).
    Com ?token=...: exibe formulário de nova senha.
    """
    token = request.query_params.get("token", "")
    return templates.TemplateResponse(
        request, "recuperar_senha.html", {"token": token}
    )


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, session: AsyncSession = Depends(get_session)):
    """Renderiza a vitrine com os produtos publicados.

    Passa também a lista de produtos em destaque (featured=True) para a seção hero.
    """
    catalog = ProductCatalog(session)
    products = await catalog.list_published()
    featured = await catalog.list_published(featured=True)
    return templates.TemplateResponse(
        request, "index.html", {"products": products, "featured": featured}
    )


@router.get("/produto/{slug}", response_class=HTMLResponse)
async def product_detail(
    request: Request,
    slug: str,
    session: AsyncSession = Depends(get_session),
):
    """Renderiza a página de detalhes de um produto (title, description, reviews).

    Levanta 404 se o produto não estiver publicado.
    """
    catalog = ProductCatalog(session)
    try:
        product = await catalog.get_by_slug(slug)
    except ProductNotFound as error:
        raise HTTPException(status_code=404, detail="Produto não encontrado") from error
    review_service = ReviewService(session)
    reviews = await review_service.list_for_product(slug)
    return templates.TemplateResponse(
        request, "produto_detalhe.html", {"product": product, "reviews": reviews}
    )


@router.post("/comprar", response_class=HTMLResponse)
async def buy(
    request: Request,
    slug: str = Form(...),
    email: str = Form(...),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    """Cria o pedido e redireciona para o checkout (simulador)."""
    catalog = ProductCatalog(session)
    checkout = CheckoutService(FakePaymentGateway(settings.base_url))
    creator = OrderCreator(session, catalog, checkout, CouponService(session, Clock()))
    try:
        order = await creator.create(slug, email)
    except ProductNotFound as error:
        raise HTTPException(status_code=404, detail="Produto não encontrado") from error
    return RedirectResponse(url=f"/pay/simulate/{order.reference}", status_code=303)


@router.get("/pay/simulate/{reference}", response_class=HTMLResponse)
def simulate_page(request: Request, reference: str):
    """Mostra a página do simulador de pagamento (aprovar/recusar)."""
    return templates.TemplateResponse(
        request, "simulate.html", {"reference": reference}
    )


@router.post("/pay/confirm/{reference}")
async def confirm_payment(
    reference: str,
    decision: str = Form("approved"),
    processor: WebhookProcessor = Depends(get_webhook_processor),
):
    """Simula a notificação do provedor e processa o pagamento (idempotente)."""
    notification = WebhookNotification(
        provider_payment_id=f"sim-{reference}",
        order_reference=reference,
        provider_status=decision,
    )
    await processor.process(notification)
    return RedirectResponse(url=f"/pedido/{reference}", status_code=303)


@router.get("/pedido/{reference}", response_class=HTMLResponse)
async def order_page(
    request: Request,
    reference: str,
    session: AsyncSession = Depends(get_session),
):
    """Mostra o status do pedido e, se pago, os links de download."""
    reader = OrderReader(session)
    try:
        order = await reader.get_by_reference(reference)
    except OrderNotFound as error:
        raise HTTPException(status_code=404, detail="Pedido não encontrado") from error

    item_ids: list[int] = []
    for item in order.items:
        item_ids.append(item.id)
    grants: list[DownloadGrant] = []
    if item_ids:
        statement = select(DownloadGrant).where(
            DownloadGrant.order_item_id.in_(item_ids)
        )
        result = await session.scalars(statement)
        grants = list(result.all())
    return templates.TemplateResponse(
        request, "order.html", {"order": order, "grants": grants}
    )
