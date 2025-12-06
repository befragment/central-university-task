from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from uuid import UUID

import jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(user_id: UUID, session_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.ACCESS_TOKEN_TTL)
    to_encode = {
        "user_id": str(user_id),
        "session_id": str(session_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def create_refresh_token(session_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.REFRESH_TOKEN_TTL)
    to_encode = {
        "session_id": str(session_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any] | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        if payload.get("type") != token_type:
            return None
        return payload
    except jwt.PyJWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)