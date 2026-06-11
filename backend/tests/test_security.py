"""Testes unitários de segurança e regras (mapper, storage, estados, token)."""

import pytest

from app.orders.models import Order, OrderStatus
from app.orders.state_machine import InvalidTransition, OrderStateMachine
from app.payments.status_map import StatusMapper, UnknownProviderStatus
from app.security.storage import PathTraversalError, ProtectedStorage
from app.security.tokens import TokenFactory


def test_status_mapper_traduz_aprovado():
    """O mapper traduz 'approved' para PAID."""
    assert StatusMapper().to_order_status("approved") == OrderStatus.PAID


def test_status_mapper_desconhecido_levanta():
    """Status desconhecido do provedor levanta erro."""
    with pytest.raises(UnknownProviderStatus):
        StatusMapper().to_order_status("???")


def test_path_traversal_bloqueado(tmp_path):
    """Tentar escapar da raiz protegida levanta PathTraversalError."""
    storage = ProtectedStorage(tmp_path)
    with pytest.raises(PathTraversalError):
        storage.resolve("../../etc/passwd")


def test_transicao_invalida_levanta():
    """Transição ilegal (paid -> paid) é rejeitada."""
    order = Order(buyer_email="x@y.com", amount=10, status=OrderStatus.PAID)
    machine = OrderStateMachine(order)
    with pytest.raises(InvalidTransition):
        machine.mark_paid()


def test_token_factory_gera_tokens_distintos():
    """Dois tokens gerados são diferentes e não vazios."""
    factory = TokenFactory()
    first = factory.generate()
    second = factory.generate()
    assert first
    assert first != second
