from fastapi import APIRouter

from api.dto import LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
) -> TokenResponse:
    return TokenResponse


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
) -> TokenResponse:
    return TokenResponse


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshTokenRequest,
) -> TokenResponse:
    return TokenResponse


@router.post("/logout", response_model=str)
async def logout(
    token: str,
) -> TokenResponse:
    return "logout"