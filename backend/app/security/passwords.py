"""Hash e verificação de senhas com PBKDF2-HMAC-SHA256 (somente stdlib)."""

import hashlib
import hmac
import secrets


class PasswordHasher:
    """Gera e verifica hashes de senha (PBKDF2), sem dependências externas."""

    def __init__(self, iterations: int = 200_000) -> None:
        """Define o número de iterações do PBKDF2 (custo de derivação)."""
        self.iterations = iterations

    def hash(self, plain: str) -> str:
        """Gera o hash no formato `pbkdf2$iteracoes$salt_hex$hash_hex`."""
        salt = secrets.token_bytes(16)
        derived = hashlib.pbkdf2_hmac(
            "sha256", plain.encode("utf-8"), salt, self.iterations
        )
        return f"pbkdf2${self.iterations}${salt.hex()}${derived.hex()}"

    def verify(self, plain: str, hashed: str) -> bool:
        """Verifica a senha contra o hash; retorna True se confere."""
        parts = hashed.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected = bytes.fromhex(parts[3])
        derived = hashlib.pbkdf2_hmac(
            "sha256", plain.encode("utf-8"), salt, iterations
        )
        return hmac.compare_digest(derived, expected)
