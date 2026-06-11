"""Schemas (Pydantic) de entrada/saída para o perfil fiscal (billing_profile)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.billing.models import PersonType


class BillingProfileIn(BaseModel):
    """Dados de entrada do perfil fiscal do usuário."""

    person_type: PersonType = PersonType.INDIVIDUAL
    legal_name: str
    document: str
    address_line: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    country: str = "BR"


class BillingProfileOut(BaseModel):
    """Representação de saída do perfil fiscal."""

    model_config = ConfigDict(from_attributes=True)

    person_type: PersonType
    legal_name: str
    document: str
    address_line: str
    city: str
    state: str
    postal_code: str
    country: str
