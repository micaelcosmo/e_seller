"""Serviço de faturamento: cria/atualiza o perfil fiscal de um usuário."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.models import BillingProfile, PersonType


class InvalidDocument(Exception):
    """Levantada quando o documento fiscal (CPF/CNPJ) é inválido."""


class BillingService:
    """Gerencia o perfil fiscal do usuário (upsert idempotente por usuário)."""

    # Comprimentos esperados de documento por tipo de pessoa (sem máscara).
    _CPF_LENGTH = 11
    _CNPJ_LENGTH = 14

    def __init__(self, session: AsyncSession) -> None:
        """Recebe a sessão de banco por injeção de dependência."""
        self.session = session

    async def get_profile(self, user_id: int) -> BillingProfile | None:
        """Retorna o perfil fiscal do usuário (ou None se ainda não existir)."""
        result = await self.session.scalars(
            select(BillingProfile).where(BillingProfile.user_id == user_id)
        )
        return result.first()

    async def upsert_profile(
        self,
        user_id: int,
        person_type: PersonType,
        legal_name: str,
        document: str,
        address_line: str = "",
        city: str = "",
        state: str = "",
        postal_code: str = "",
        country: str = "BR",
    ) -> BillingProfile:
        """Cria ou atualiza o perfil fiscal do usuário, validando o documento."""
        clean_document = self._normalize_document(document, person_type)
        profile = await self.get_profile(user_id)
        if profile is None:
            profile = BillingProfile(user_id=user_id)
            self.session.add(profile)
        profile.person_type = person_type
        profile.legal_name = legal_name.strip()
        profile.document = clean_document
        profile.address_line = address_line.strip()
        profile.city = city.strip()
        profile.state = state.strip().upper()
        profile.postal_code = self._only_digits(postal_code)
        profile.country = (country or "BR").strip().upper()
        await self.session.flush()
        return profile

    def _normalize_document(self, document: str, person_type: PersonType) -> str:
        """Remove a máscara e valida o tamanho do CPF/CNPJ conforme o tipo."""
        digits = self._only_digits(document)
        expected = self._CPF_LENGTH
        if person_type == PersonType.COMPANY:
            expected = self._CNPJ_LENGTH
        if len(digits) != expected:
            raise InvalidDocument(document)
        return digits

    def _only_digits(self, value: str) -> str:
        """Mantém apenas os dígitos de um texto (remove máscara)."""
        digits = ""
        for character in value:
            if character.isdigit():
                digits = digits + character
        return digits
