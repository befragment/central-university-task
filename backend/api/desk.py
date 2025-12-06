from uuid import UUID
from http import HTTPStatus
from fastapi import APIRouter, Depends, Query, HTTPException

from api.dependencies import get_current_user, get_desk_repo, get_deskshare_repo
from pydantic import UUID4
from http import HTTPStatus

from fastapi import APIRouter, Query, Depends, HTTPException, Response

from model.user import User as UserORM
from api.dependencies import get_current_user, get_desk_repo
from api.dto import (
    Desk, 
    DeskCreateRequest, 
    DesksResponseWithTotal,
    DeskUpdateRequest,
    Share, Shares,
    UserDTO
)
from model import User
from repository import DeskRepository
from repository import DeskShareRepository
)

from repository import DeskRepository

router = APIRouter(prefix="/desks", tags=["desks"])

@router.post("/", response_model=Desk)
async def create_desk(
    request: DeskCreateRequest,
    desk_repo: DeskRepository = Depends(get_desk_repo),
    current_user: UserORM = Depends(get_current_user),
):
    desk = await desk_repo.create(
        name=request.name,
        owner_id=current_user.id,
    )
    return desk


@router.delete("/{desk_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_desk(
    desk_id: UUID4,
    desk_repo: DeskRepository = Depends(get_desk_repo),
    current_user: UserORM = Depends(get_current_user),
):
    desk = await desk_repo.get_by_id(
        desk_id=desk_id,
    )

    if desk is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    
    if desk.owner_id != current_user.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

    result = await desk_repo.delete(
        desk_id=desk_id,
    )

    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.patch("/{desk_id}", response_model=Desk)
async def update_desk(
    desk_id: UUID4,
    request: DeskUpdateRequest,
    desk_repo: DeskRepository = Depends(get_desk_repo),
    current_user: UserORM = Depends(get_current_user),
):
    desk = await desk_repo.get_by_id(desk_id=desk_id)

    if desk is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    
    if desk.owner_id != current_user.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

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

    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

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





