from http import HTTPStatus
from fastapi import APIRouter

from api.dto import (
    Tokens,
    LoginRequest,
    LoginResponse, 
    RegisterRequest, 
    LoginResponse, 
    RefreshTokenRequest
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
) -> LoginResponse:
    return LoginResponse


@router.post("/register", status_code=HTTPStatus.NO_CONTENT)
async def register(
    request: RegisterRequest,
):
    return 


@router.post("/refresh", response_model=Tokens)
async def refresh(
    request: RefreshTokenRequest,
) -> Tokens:
    return Tokens


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def logout(
    token: str,
):
    return 