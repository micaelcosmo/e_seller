"""Testes SEC-18: audit log de ações administrativas."""

from __future__ import annotations

from app.accounts.models import User, UserRole
from app.admin.audit import AdminAuditLog, AdminAuditService
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session, email: str) -> str:
    """Cria conta staff e retorna token JWT."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(email=email, password_hash=hasher.hash("pw"), role=UserRole.STAFF)
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token", data={"username": email, "password": "pw"}
    )
    return resp.json()["access_token"]


async def test_audit_service_cria_entrada(db_session) -> None:
    """AdminAuditService.log() deve persistir entrada no banco."""
    service = AdminAuditService(db_session)
    entry = await service.log(
        actor_email="admin@sec18.com",
        action="delete",
        resource_type="product",
        resource_id="42",
        detail="removido por conteúdo inválido",
    )
    await db_session.commit()
    assert entry.id is not None
    assert entry.actor_email == "admin@sec18.com"
    assert entry.action == "delete"
    assert entry.resource_type == "product"


async def test_moderate_review_grava_audit_log(client, db_session) -> None:
    """PATCH /admin/reviews/{id}/moderate deve criar entrada no audit log."""
    from decimal import Decimal

    from app.accounts.models import User as UserModel
    from app.catalog.models import Product, ProductStatus
    from app.reviews.models import Review, ReviewStatus

    token = await _staff_token(client, db_session, "mod@sec18.com")

    reviewer = UserModel(
        email="reviewer@sec18.com",
        password_hash=PasswordHasher(iterations=1000).hash("pw"),
        role=UserRole.CUSTOMER,
    )
    db_session.add(reviewer)
    await db_session.flush()

    product = Product(
        title="Livro SEC18",
        slug="livro-sec18",
        price=Decimal("10.00"),
        status=ProductStatus.PUBLISHED,
    )
    db_session.add(product)
    await db_session.flush()

    review = Review(
        product_id=product.id,
        user_id=reviewer.id,
        rating=4,
        comment="Muito bom.",
        status=ReviewStatus.PENDING,
    )
    db_session.add(review)
    await db_session.commit()

    resp = await client.patch(
        f"/api/v1/admin/reviews/{review.id}/moderate",
        json={"status": "approved"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    from sqlalchemy import select
    result = await db_session.scalars(
        select(AdminAuditLog).where(
            AdminAuditLog.resource_type == "review",
            AdminAuditLog.resource_id == str(review.id),
        )
    )
    log_entry = result.first()
    assert log_entry is not None
    assert log_entry.action == "moderate"
    assert log_entry.detail == "approved"


async def test_create_coupon_grava_audit_log(client, db_session) -> None:
    """POST /admin/coupons deve criar entrada no audit log."""
    from sqlalchemy import select

    token = await _staff_token(client, db_session, "coupon@sec18.com")
    resp = await client.post(
        "/api/v1/admin/coupons",
        json={
            "code": "SEC18TEST",
            "discount_type": "percent",
            "value": "10.00",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201

    result = await db_session.scalars(
        select(AdminAuditLog).where(
            AdminAuditLog.resource_type == "coupon",
            AdminAuditLog.resource_id == "SEC18TEST",
        )
    )
    log_entry = result.first()
    assert log_entry is not None
    assert log_entry.action == "create"
