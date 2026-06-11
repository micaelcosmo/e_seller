"""Emissão e validação de JWT HS256 usando apenas a biblioteca padrão."""

import base64
import hashlib
import hmac
import json
import time


class InvalidToken(Exception):
    """Levantada quando o token é malformado ou tem assinatura inválida."""


class ExpiredToken(InvalidToken):
    """Levantada quando o token está expirado."""


class JwtService:
    """Emite e valida JWT HS256 (stdlib), com expiração configurável.

    Distingue dois tipos de token: access (curto prazo) e refresh (longo prazo).
    O payload do refresh token carrega `type='refresh'` para evitar uso indevido.
    """

    _RESET_TTL_SECONDS = 3600

    def __init__(
        self,
        secret_key: str,
        ttl_seconds: int = 3600,
        refresh_ttl_seconds: int = 604_800,
    ) -> None:
        """Recebe a chave secreta e os tempos de vida dos tokens."""
        self.secret_key = secret_key
        self.ttl_seconds = ttl_seconds
        self.refresh_ttl_seconds = refresh_ttl_seconds

    def issue(self, subject: str, now: int | None = None) -> str:
        """Emite um access token JWT para o `subject`, com `iat`/`exp`."""
        issued = now if now is not None else int(time.time())
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {"sub": subject, "iat": issued, "exp": issued + self.ttl_seconds}
        signing_input = f"{self._encode(header)}.{self._encode(payload)}"
        signature = self._sign(signing_input)
        return f"{signing_input}.{signature}"

    def issue_refresh(self, subject: str, now: int | None = None) -> str:
        """Emite um refresh token JWT (TTL longo, `type='refresh'`)."""
        issued = now if now is not None else int(time.time())
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": subject,
            "iat": issued,
            "exp": issued + self.refresh_ttl_seconds,
            "type": "refresh",
        }
        signing_input = f"{self._encode(header)}.{self._encode(payload)}"
        signature = self._sign(signing_input)
        return f"{signing_input}.{signature}"

    def verify(self, token: str, now: int | None = None) -> dict:
        """Valida assinatura e expiração; retorna os claims ou levanta erro."""
        current = now if now is not None else int(time.time())
        parts = token.split(".")
        if len(parts) != 3:
            raise InvalidToken("formato inválido")
        signing_input = f"{parts[0]}.{parts[1]}"
        expected = self._sign(signing_input)
        if not hmac.compare_digest(expected, parts[2]):
            raise InvalidToken("assinatura inválida")
        payload = json.loads(self._decode(parts[1]))
        if int(payload.get("exp", 0)) < current:
            raise ExpiredToken("token expirado")
        return payload

    def verify_refresh(self, token: str, now: int | None = None) -> str:
        """Valida refresh token; retorna subject ou levanta InvalidToken."""
        claims = self.verify(token, now)
        if claims.get("type") != "refresh":
            raise InvalidToken("não é um refresh token")
        sub = claims.get("sub")
        if not sub:
            raise InvalidToken("subject ausente")
        return sub

    def issue_reset(self, email: str, now: int | None = None) -> str:
        """Emite token de redefinição de senha com TTL de 1 hora (`type='reset'`)."""
        issued = now if now is not None else int(time.time())
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": email,
            "iat": issued,
            "exp": issued + self._RESET_TTL_SECONDS,
            "type": "reset",
        }
        signing_input = f"{self._encode(header)}.{self._encode(payload)}"
        signature = self._sign(signing_input)
        return f"{signing_input}.{signature}"

    def verify_reset(self, token: str, now: int | None = None) -> str:
        """Valida token de redefinição; retorna e-mail ou levanta InvalidToken."""
        claims = self.verify(token, now)
        if claims.get("type") != "reset":
            raise InvalidToken("não é um token de redefinição de senha")
        sub = claims.get("sub")
        if not sub:
            raise InvalidToken("subject ausente")
        return sub

    def _encode(self, data: dict) -> str:
        """Serializa um dicionário e codifica em base64url (sem padding)."""
        raw = json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    def _decode(self, segment: str) -> bytes:
        """Decodifica um segmento base64url (restaurando o padding)."""
        padding = "=" * (-len(segment) % 4)
        return base64.urlsafe_b64decode(segment + padding)

    def _sign(self, signing_input: str) -> str:
        """Assina o input com HMAC-SHA256 e retorna em base64url."""
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            signing_input.encode("ascii"),
            hashlib.sha256,
        ).digest()
        return base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
