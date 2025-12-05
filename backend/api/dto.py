import typing

from pydantic import BaseModel, EmailStr, Field, UUID4

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="The email of the user")
    password: str = Field(..., description="The password of the user")


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="The email of the user")
    password: str = Field(..., description="The password of the user")
    name: str = Field(..., description="The name of the user")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="The refresh token")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="The access token")
    refresh_token: str = Field(..., description="The refresh token")


class DeskCreateRequest(BaseModel):
    name: str = Field(..., description="Desk name")


class DeskCreateResponse(BaseModel):
    name: str = Field(..., description="Desk name")


class DeskDeleteRequest(BaseModel):
    id: UUID4 = Field(..., description="Desk id")


class DeskDeleteResponse(BaseModel):
    id: UUID4 = Field(..., description="Desk id")


class DeskUpdateRequest(BaseModel):
    id: UUID4 = Field(..., description="Desk id")
    name: typing.Optional[str | None] = Field(..., description="Desk name")


class DeskUpdateResponse(BaseModel):
    id: UUID4 = Field(..., description="Desk id")
    name: typing.Optional[str | None] = Field(..., description="Desk name")