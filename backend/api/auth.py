from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_session_repo, get_user_repo
from core.database import get_db
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)

from repository.user import UserRepository
from repository.session import SessionRepository

from model.user import User as UserModel
from model.session import Session as SessionModel

from api.dto import (
    User,
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
    user_repo: UserRepository = Depends(get_user_repo)
) -> None:
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
    # 201 Created — no content


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repo),
    session_repo: SessionRepository = Depends(get_session_repo)
) -> LoginResponse:
    user = await user_repo.get_by_email(request.email)
    if not user or not verify_password(request.password, user.pass_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_CREDENTIALS", "message": "Неверный email или пароль"}
        )

    db_session = await session_repo.create(user.id)

    access_token = create_access_token(user.id, db_session.id)
    refresh_token = create_refresh_token(db_session.id)

    return LoginResponse(
        user=User(  # если это твой Pydantic User DTO
            id=user.id,
            name=user.name,
            email=user.email,
        ),
        access_token=access_token,
        refresh_token=refresh_token,
    )

@router.post("/refresh", response_model=Tokens)
async def refresh(
    request: RefreshTokenRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Tokens:
    payload = verify_token(request.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_TOKEN", "message": "Токен недействителен или истёк"}
        )

    try:
        session_id = UUID(payload["session_id"])
    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_TOKEN", "message": "Некорректный формат токена"}
        )

    db_session = await session.get(SessionModel, session_id)
    if not db_session or not db_session.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_TOKEN", "message": "Токен недействителен или истёк"}
        )

    user_id = db_session.user_id

    session_repo = SessionRepository(session)
    await session_repo.deactivate(session_id)
    new_session = await session_repo.create(user_id)

    access_token = create_access_token(user_id, new_session.id)
    refresh_token = create_refresh_token(new_session.id)

    return Tokens(access_token=access_token, refresh_token=refresh_token)


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
