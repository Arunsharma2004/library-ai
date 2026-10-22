"""Password hashing using only Python's standard library."""
import hashlib
import hmac
import os

ITERATIONS = 600_000  # deliberately slow, which makes guessing passwords expensive


def hash_password(password: str) -> str:
    salt = os.urandom(16)  # a random value, so equal passwords get different hashes
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"{ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        iterations, salt_hex, digest_hex = stored.split("$")
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex(), digest_hex)  # safe against timing attacks