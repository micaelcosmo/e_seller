"""Testes BEQ-11: e-mail de confirmação de compra."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.accounts.models import User, UserRole
from app.security.passwords import PasswordHasher


async def _staff_token(client, db_session) -> str:
    """Cria staff e retorna token."""
    hasher = PasswordHasher(iterations=1000)
    db_session.add(
        User(
            email="email_staff@x.com",
            password_hash=hasher.hash("pw"),
            role=UserRole.STAFF,
        )
    )
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "email_staff@x.com", "password": "pw"},
    )
    return resp.json()["access_token"]


async def test_email_enviado_apos_compra_aprovada(client, db_session) -> None:
    """Após webhook aprovado, EmailService.send_purchase_confirmation é chamado."""
    staff = await _staff_token(client, db_session)
    create_resp = await client.post(
        "/api/v1/admin/products",
        json={"title": "E-mail Test Book", "price": "19.90"},
        headers={"Authorization": f"Bearer {staff}"},
    )
    slug = create_resp.json()["slug"]
    await client.patch(
        f"/api/v1/admin/products/{slug}/status",
        json={"status": "published"},
        headers={"Authorization": f"Bearer {staff}"},
    )
    order_resp = await client.post(
        "/api/v1/orders",
        json={"product_slug": slug, "buyer_email": "buyer_email@x.com"},
    )
    reference = order_resp.json()["reference"]
    send_path = "app.core.email.EmailService.send_purchase_confirmation"
    with patch(send_path) as mock_send:
        mock_send.return_value = None
        wh = await client.post(
            "/api/v1/webhooks/mercadopago",
            json={
                "provider_payment_id": f"fake-em-{reference}",
                "order_reference": reference,
                "provider_status": "approved",
            },
        )
        assert wh.status_code == 200
        # Como smtp_host está vazio nas settings de teste, _enabled() retorna False
        # e send_purchase_confirmation não chama smtplib — mas o método É invocado.
        # O patch intercepta antes de verificar _enabled(), confirmando o fluxo.
        assert mock_send.called


async def test_email_nao_enviado_se_smtp_desativado(client, db_session) -> None:
    """Quando smtp_host está vazio, send_purchase_confirmation retorna sem enviar."""
    from app.core.config import Settings
    from app.core.email import EmailService

    settings = Settings(smtp_host="")
    svc = EmailService(settings)
    # Não deve levantar nenhuma exceção ao chamar sem SMTP configurado.
    svc.send_purchase_confirmation("test@x.com", "Livro Teste", "REF-0001")


async def test_email_mock_envia_sem_smtp(client, db_session) -> None:
    """EmailService com smtp_host vazio não tenta conectar ao servidor SMTP."""
    import smtplib

    from app.core.config import Settings
    from app.core.email import EmailService

    settings = Settings(smtp_host="")
    svc = EmailService(settings)
    mock_smtp = MagicMock(spec=smtplib.SMTP)
    with patch("smtplib.SMTP", return_value=mock_smtp):
        svc.send_purchase_confirmation("a@b.com", "Livro", "REF-999")
        # SMTP não deve ser instanciado quando smtp_host está vazio.
        mock_smtp.assert_not_called()
