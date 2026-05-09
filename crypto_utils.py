from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from typing import Any, Dict

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


PBKDF2_ITERATIONS = 390_000
SALT_SIZE = 16
NONCE_SIZE = 12 
KEY_SIZE = 32   


class VaultCryptoError(Exception):
    """Raised when vault decryption fails, usually because the master password is wrong."""
@dataclass
class VaultPackage:
    salt: str
    nonce: str
    ciphertext: str
    kdf: str = "PBKDF2HMAC-SHA256"
    iterations: int = PBKDF2_ITERATIONS
    algorithm: str = "AES-256-GCM"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "algorithm": self.algorithm,
            "kdf": self.kdf,
            "iterations": self.iterations,
            "salt": self.salt,
            "nonce": self.nonce,
            "ciphertext": self.ciphertext,
        }



def _b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")



def _b64decode(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


def derive_key(master_password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    """Derive a strong AES key from the user's master password."""
    if not master_password:
        raise ValueError("Master password cannot be empty.")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(master_password.encode("utf-8"))

def encrypt_vault(vault_data: Dict[str, Any], master_password: str, existing_salt: str | None = None) -> Dict[str, Any]:
    """Encrypt the full vault dictionary using AES-256-GCM."""
    salt = _b64decode(existing_salt) if existing_salt else os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(master_password, salt)
    aesgcm = AESGCM(key)

    plaintext = json.dumps(vault_data, ensure_ascii=False, indent=2).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)

    return VaultPackage(
        salt=_b64encode(salt),
        nonce=_b64encode(nonce),
        ciphertext=_b64encode(ciphertext),
    ).to_dict()
