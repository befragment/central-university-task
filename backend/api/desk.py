from uuid import UUID
from http import HTTPStatus
from fastapi import APIRouter, Depends, Query, HTTPException

from api.dependencies import get_current_user, get_desk_repo, get_deskshare_repo
from api.dto import (
    Desk,
    DeskCreateRequest, 
    DeskDeleteRequest, 
    DeskDeleteResponse,
    DesksResponseWithTotal,
    SharedDesksWithTotal, 
    DeskUpdateRequest,
    Share, Shares,
    UserDTO
)
from model import User
from repository import DeskRepository
from repository import DeskShareRepository

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
async def get_desk_shares(
    desk_id: UUID,
    current_user: User = Depends(get_current_user),
    desk_repo: DeskRepository = Depends(get_desk_repo),
    deskshare_repo: DeskShareRepository = Depends(get_deskshare_repo),
):
    is_owned = await desk_repo.is_owned_by_user(desk_id, current_user.id)
    if not is_owned:
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    shares_rows = await deskshare_repo.get_shares_with_users(desk_id)

    return Shares(
        shares=[
            Share(
                id=row.id,
                user=UserDTO(
                    id=row.user.id,
                    name=row.user.name,
                    email=row.user.email,
                ),
                created_at=row.created_at,
            )
            for row in shares_rows
        ]
    )


@router.post("/{desk_id}/shares", response_model=Share)
async def share_desk_with_user(
    desk_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    desk_repo: DeskRepository = Depends(get_desk_repo),
    deskshare_repo: DeskShareRepository = Depends(get_deskshare_repo)
):
    is_owned = await desk_repo.is_owned_by_user(desk_id, current_user.id)
    if not is_owned:
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    row = await deskshare_repo.add_user_to_desk_share(desk_id, user_id)

    return Share(
        id=row.id,
        user=UserDTO(
            id=row.user.id,
            name=row.user.name,
            email=row.user.email,
        ),
        created_at=row.created_at,
    )


@router.delete("/{desk_id}/shares/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def revoke_desk_access(
    desk_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    desk_repo: DeskRepository = Depends(get_desk_repo),
    deskshare_repo: DeskShareRepository = Depends(get_deskshare_repo)
):
    is_owned = desk_repo.is_owned_by_user(desk_id, current_user.id)
    if not is_owned:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="CANNOT_REVOKE_OWNER")
    
    await deskshare_repo.delete_user_from_desk_share(desk_id, user_id)





