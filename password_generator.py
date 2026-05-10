"""Secure password generator."""

from __future__ import annotations

import secrets
import string


def generate_password(length: int = 16) -> str:
    """Generate a strong password containing upper/lowercase letters, digits, and symbols."""
    if length < 12:
        length = 12

    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{};:,.?/"
    all_chars = lowercase + uppercase + digits + symbols

    # Guarantee at least one character from each group.
    password_chars = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(symbols),
    ]

    password_chars.extend(secrets.choice(all_chars) for _ in range(length - len(password_chars)))
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)