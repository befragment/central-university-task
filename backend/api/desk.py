from http import HTTPStatus
from fastapi import APIRouter, Depends, Query

from api.dependencies import get_current_user
from api.dto import (
    Desk,
    DeskCreateRequest, 
    DeskDeleteRequest, 
    DeskDeleteResponse,
    DesksResponseWithTotal,
    SharedDesksWithTotal, 
    DeskUpdateRequest,
    Share, Shares,
)
from model import User

router = APIRouter(prefix="/desks", tags=["desks"])

@router.post("/", response_model=Desk)
async def create_desk(
    request: DeskCreateRequest,
):
    return Desk


@router.delete("/", response_model=DeskDeleteResponse)
async def delete_desk(
    request: DeskDeleteRequest,
    current_user: User = Depends(get_current_user)
):
    return DeskDeleteResponse


@router.patch("/{desk_id}", response_model=Desk)
async def update_desk(
    request: DeskUpdateRequest
):
    return Desk


@router.get("/", response_model=DesksResponseWithTotal)
async def get_my_desks():
    return DesksResponseWithTotal


@router.get("/shared", response_model=SharedDesksWithTotal)
async def get_shared_desks(
    limit: int = Query(5, ge=0, le=100),
    offset: int = Query(0, ge=0),
):
    return SharedDesksWithTotal


@router.get("/{desk_id}/shares", response_model=Shares)
async def get_shares_of_desk():
    return Shares


@router.post("/{desk_id}/shares", response_model=Share)
async def share_desk_with_user():
    return Share


@router.delete("/{desk_id}/shares/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def revoke_desk_access(
    desk_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    ...
