from typing import Any

from repository import UserRepository
from core.security import (
    verify_password,
    verify_token,
    create_access_token,
    create_refresh_token,
    get_password_hash,
)
from model.user import User
from service.exception import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    InvalidAccessTokenError,
)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def login(self, email: str, password: str) -> dict[str, Any]:
        user = await self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user.password):
            raise InvalidCredentialsError

        payload = {"sub": str(user.id), "email": user.email}
        access = create_access_token(payload)
        refresh = create_refresh_token(payload)

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
        }

    async def register(
        self,
        email: str,
        password: str,
        direction: str,
        name: str,
        company_id: int | None,
    ) -> dict[str, Any]:
        existing = await self.user_repository.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError

        password_hash = get_password_hash(password)

        # Normalize company_id: treat 0 or negative as None (candidate without company)
        normalized_company_id: int | None
        if company_id is None or (isinstance(company_id, int) and company_id <= 0):
            normalized_company_id = None
        else:
            normalized_company_id = company_id

        user = User(
            email=email,
            password=password_hash,
            direction=direction,
            name=name,
            company_id=normalized_company_id,
        )
        user = await self.user_repository.create(user)

        payload = {"sub": str(user.id), "email": user.email, "role": ""}
        access = create_access_token(payload)
        refresh = create_refresh_token(payload)

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
        }

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        payload = verify_token(refresh_token, "refresh")
        if not payload:
            raise InvalidRefreshTokenError

        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidRefreshTokenError

        user = await self.user_repository.get_by_id(int(user_id))
        if not user:
            raise UserNotFoundError

        base_payload = {k: v for k, v in payload.items() if k not in ("exp", "type")}

        access = create_access_token(base_payload)
        new_refresh = create_refresh_token(base_payload)

        return {
            "access_token": access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }

    async def get_current_user(self, token: str) -> User | None:
        payload = verify_token(token, "access")
        if not payload:
            return None

        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidAccessTokenError

        try:
            user_id_int = int(user_id)
        except (TypeError, ValueError):
            raise InvalidAccessTokenError

        return await self.user_repository.get_by_id(user_id_int)
