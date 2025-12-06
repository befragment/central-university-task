import typing
import datetime

from pydantic import BaseModel, EmailStr, UUID4


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class User(BaseModel):
    id: UUID4
    name: str
    email: EmailStr


class Users(BaseModel):
    users: list[User]


class RefreshTokenRequest(BaseModel):
    refresh_token: str 


class Tokens(BaseModel):
    access_token: str
    refresh_token: str 


class LoginResponse(BaseModel):
    user: User
    access_token: str
    refresh_token: str


class DeskCreateRequest(BaseModel):
    name: str


class DeskCreateResponse(BaseModel):
    name: str


class DeskDeleteRequest(BaseModel):
    id: UUID4


class DeskDeleteResponse(BaseModel):
    id: UUID4


class DeskUpdateRequest(BaseModel):
    name: typing.Optional[str | None]


class DeskUpdateResponse(BaseModel):
    id: UUID4
    name: typing.Optional[str | None]


class Desk(BaseModel):
    id: UUID4
    name: str
    owner_id: UUID4
    created_at: datetime.datetime
    updated_at: datetime.datetime


class DesksResponseWithTotal(BaseModel):
    desks: list[Desk]
    total: int


class DeskOwner(BaseModel):
    id: UUID4
    name: str


class SharedDesk(BaseModel):
    # This entity is still desk
    id: UUID4
    name: str
    owner: DeskOwner
    shared_at: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime


class SharedDesksWithTotal(BaseModel):
    shares: list[SharedDesk]
    total: int


class Share(BaseModel):
    # Share as an entity 
    id: UUID4
    user: User
    created_at: datetime.datetime


class Shares(BaseModel):
    shares: list[Share]


class UserIDRequest(BaseModel):
    id: UUID4