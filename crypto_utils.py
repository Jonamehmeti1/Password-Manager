
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