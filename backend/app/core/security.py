"""
CORE SECURITY: Sanitization, Password Hashing & JWT Authentication
==================================================================
Handles input scrubbing, bcrypt password hashing, and JWT tokens.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import jwt, JWTError

from backend.app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Prompt injection and malicious patterns to neutralize
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions",
    r"disregard\s+(?:all\s+)?(?:previous\s+)?commands",
    r"system\s*:\s*",
    r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
    r"javascript\s*:",
    r"onload\s*=",
    r"onerror\s*=",
]


def sanitize_input(text: str) -> str:
    """
    Sanitizes user input by stripping HTML tags, script elements,
    and neutralizing prompt injection tokens.
    """
    if not text:
        return ""

    # Strip HTML tags
    cleaned = re.sub(r"<[^>]+>", "", text)

    # Neutralize prompt injection phrases
    for pattern in PROMPT_INJECTION_PATTERNS:
        cleaned = re.sub(pattern, "[FILTERED]", cleaned, flags=re.IGNORECASE)

    # Strip excess whitespace
    return " ".join(cleaned.split())


def hash_password(password: str) -> str:
    """Generates bcrypt password hash."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a signed JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
