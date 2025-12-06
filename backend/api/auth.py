from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from core.config import settings

from repository.user import UserRepository
from repository.session import SessionRepository

from model.user import User as UserModel
from model.session import Session as SessionModel

from api.dto import (
    Tokens,
    LoginRequest,
    LoginResponse, 
    RegisterRequest, 
    LoginResponse, 
    RefreshTokenRequest
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    user_repo = UserRepository(session)
    existing = await user_repo.get_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "USER_EXISTS", "message": "Пользователь с таким email уже существует"}
        )

    hashed_pw = get_password_hash(request.password)
    new_user = UserModel(
        name=request.name,
        email=request.email,
        pass_hash=hashed_pw,
    )
    await user_repo.create(new_user)
    return  # 201 Created — no content


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_email(request.email)
    if not user or not verify_password(request.password, user.pass_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_CREDENTIALS", "message": "Неверный email или пароль"}
        )

    # Создаём новую сессию
    session_repo = SessionRepository(session)
    db_session = await session_repo.create(user.id)

    # Подготавливаем payload для токенов
    token_data = {
        "user_id": str(user.id),
        "session_id": str(db_session.id),
    }

    access_token = create_access_token(
        data=token_data,
        expires_delta=None  # будет использован settings.ACCESS_TOKEN_TTL
    )
    refresh_token = create_refresh_token(data=token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Tokens)
async def refresh(
    request: RefreshTokenRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    payload = verify_token(request.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_TOKEN", "message": "Токен недействителен или истёк"}
        )

    try:
        user_id = UUID(payload["user_id"])
        session_id = UUID(payload["session_id"])
    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_TOKEN", "message": "Некорректный формат токена"}
        )

    # Проверяем, существует ли сессия и активна ли она
    result = await session.get(SessionModel, session_id)
    db_session: SessionModel | None = result

    if not db_session or not db_session.is_active or db_session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_TOKEN", "message": "Токен недействителен или истёк"}
        )

    # Ротация refresh-токена: деактивируем старую сессию , создаём новую
    session_repo = SessionRepository(session)
    await session_repo.deactivate(session_id)
    new_session = await session_repo.create(user_id)

    # Генерируем новые токены
    new_token_data = {
        "user_id": str(user_id),
        "session_id": str(new_session.id),
    }

    access_token = create_access_token(data=new_token_data)
    refresh_token = create_refresh_token(data=new_token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: RefreshTokenRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    payload = verify_token(request.refresh_token, token_type="refresh")
    if not payload:
        # Согласно REST - logout идемпотентен: не ошибка, если токен невалиден
        return

    try:
        session_id = UUID(payload["session_id"])
    except (ValueError, KeyError, TypeError):
        return  # игнорируем - нет сессии для деактивации

    session_repo = SessionRepository(session)
    await session_repo.deactivate(session_id)

    return  # 204 No Content
