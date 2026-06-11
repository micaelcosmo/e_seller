"""Testes de autenticação: hash de senha (PBKDF2) e JWT (HS256)."""

import pytest

from app.security.jwt import ExpiredToken, InvalidToken, JwtService
from app.security.passwords import PasswordHasher


def test_password_hash_e_verifica():
    """O hash gerado é verificável com a senha correta."""
    hasher = PasswordHasher(iterations=1000)
    hashed = hasher.hash("segredo")
    assert hasher.verify("segredo", hashed)
    assert not hasher.verify("errado", hashed)


def test_password_hash_unico_por_salt():
    """Dois hashes da mesma senha diferem (salt aleatório)."""
    hasher = PasswordHasher(iterations=1000)
    assert hasher.hash("igual") != hasher.hash("igual")


def test_password_hash_malformado_retorna_false():
    """Verificação contra hash malformado retorna False (sem erro)."""
    hasher = PasswordHasher(iterations=1000)
    assert not hasher.verify("x", "formato-invalido")


def test_jwt_emite_e_valida():
    """O JWT emitido é validado e expõe o subject."""
    service = JwtService("chave", ttl_seconds=3600)
    token = service.issue("admin@e_seller", now=1000)
    claims = service.verify(token, now=1001)
    assert claims["sub"] == "admin@e_seller"


def test_jwt_expirado_levanta():
    """Token além do prazo de expiração é rejeitado."""
    service = JwtService("chave", ttl_seconds=60)
    token = service.issue("u", now=1000)
    with pytest.raises(ExpiredToken):
        service.verify(token, now=2000)


def test_jwt_adulterado_levanta():
    """Assinatura adulterada é rejeitada."""
    service = JwtService("chave", ttl_seconds=60)
    token = service.issue("u", now=1000)
    tampered = token[:-3] + ("aaa" if not token.endswith("aaa") else "bbb")
    with pytest.raises(InvalidToken):
        service.verify(tampered, now=1001)


def test_jwt_chave_errada_levanta():
    """Token assinado com outra chave é rejeitado."""
    token = JwtService("chave-a", ttl_seconds=60).issue("u", now=1000)
    with pytest.raises(InvalidToken):
        JwtService("chave-b", ttl_seconds=60).verify(token, now=1001)
