import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import verify_token
from model import User
from repository import (
    DeskShareRepository,
    DeskDetailRepository,
    UserRepository, 
    DeskRepository,
    SessionRepository
)

async def get_deskshare_repo(session: AsyncSession = Depends(get_db)):
    return DeskShareRepository(session)

async def get_deskdetail_repo(session: AsyncSession = Depends(get_db)):
    return DeskDetailRepository(session)

async def get_user_repo(session: AsyncSession = Depends(get_db)):
    return UserRepository(session)

async def get_desk_repo(session: AsyncSession = Depends(get_db)):
    return DeskRepository(session)

async def get_session_repo(session: AsyncSession = Depends(get_db)):
    return SessionRepository(session)


bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    repo: UserRepository = Depends(get_user_repo),
) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = credentials.credentials

    # Если твои access-токены реально содержат type="access", оставь так:
    payload = verify_token(token, token_type="access")

    # Если НЕ содержат type, то временно на хакатон можно так:
    # payload = verify_token(token, token_type="access") or verify_token(token, token_type="refresh")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id_raw = payload.get("user_id")
    if not user_id_raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = uuid.UUID(str(user_id_raw))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id",
        )

    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user