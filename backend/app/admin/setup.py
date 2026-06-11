"""Montagem do painel SQLAdmin na aplicação FastAPI."""

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine

from app.admin.auth import AdminAuth
from app.admin.views import (
    AuthorAdmin,
    BillingProfileAdmin,
    CategoryAdmin,
    CouponAdmin,
    DownloadGrantAdmin,
    OrderAdmin,
    PaymentAdmin,
    ProductAdmin,
    ProductFileAdmin,
    ProductImageAdmin,
    PublisherAdmin,
    RefundAdmin,
    ReviewAdmin,
    SeriesAdmin,
    TagAdmin,
    UserAdmin,
)


def setup_admin(app: FastAPI, engine: AsyncEngine, auth_backend: AdminAuth) -> Admin:
    """Monta o SQLAdmin e registra as views administrativas."""
    admin = Admin(
        app,
        engine,
        authentication_backend=auth_backend,
        title="e_seller — Admin",
    )
    admin.add_view(ProductAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(AuthorAdmin)
    admin.add_view(PublisherAdmin)
    admin.add_view(SeriesAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(ProductFileAdmin)
    admin.add_view(ProductImageAdmin)
    admin.add_view(CouponAdmin)
    admin.add_view(OrderAdmin)
    admin.add_view(PaymentAdmin)
    admin.add_view(RefundAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(BillingProfileAdmin)
    admin.add_view(ReviewAdmin)
    admin.add_view(DownloadGrantAdmin)
    return admin
