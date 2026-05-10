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

def save_vault(vault_data: Dict[str, Any], master_password: str, path: Path = DEFAULT_VAULT_PATH) -> None:
    existing_salt = None
    if path.exists():
        try:
            existing_salt = load_package(path).get("salt")
        except Exception:
            existing_salt = None
    package = encrypt_vault(vault_data, master_password, existing_salt=existing_salt)
    save_package(package, path) 

def load_package(path: Path = DEFAULT_VAULT_PATH) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Vault file not found: {path}")   
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
    
    
def save_package(package: Dict[str, Any], path: Path = DEFAULT_VAULT_PATH) -> None: