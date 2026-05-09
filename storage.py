from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict

from crypto_utils import decrypt_vault, encrypt_vault