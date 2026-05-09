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
