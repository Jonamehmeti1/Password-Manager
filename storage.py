from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict

from crypto_utils import decrypt_vault, encrypt_vault

DEFAULT_VAULT_PATH = Path("vault.enc")

def create_empty_vault(master_password: str, path: Path = DEFAULT_VAULT_PATH) -> Dict[str, Any]:
    vault_data = {"entries": []}
    package = encrypt_vault(vault_data, master_password)
    save_package(package, path)
    return vault_data

def load_vault(master_password: str, path: Path = DEFAULT_VAULT_PATH) -> Dict[str, Any]:
    package = load_package(path)
    return decrypt_vault(package, master_password)
