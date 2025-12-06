from pydantic import UUID4
from http import HTTPStatus

from fastapi import APIRouter, Query, Depends, HTTPException, Response

from model.user import User as UserORM
from api.dependencies import get_current_user, get_desk_repo
from api.dto import (
    Desk, DeskOut, 
    DeskCreateRequest, 
    DesksResponseWithTotal,
    DeskUpdateRequest,
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

    result = await desk_repo.update(
        desk_id=desk_id,
        name=request.name,
    )

    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    updated_desk = await desk_repo.get_by_id(desk_id=desk_id)
    return updated_desk


@router.get("/", response_model=DesksResponseWithTotal)
async def get_my_desks(
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0),
    desk_repo: DeskRepository = Depends(get_desk_repo),
    current_user: UserORM = Depends(get_current_user),
):
    total = await desk_repo.count_owned_by_user(current_user.id)
    desks = await desk_repo.get_owned_by_user_paginated(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    desks_out = [DeskOut.model_validate(d) for d in desks]

    return DesksResponseWithTotal(
        desks=desks_out,
        total=total,
    )

# @router.get("/shared", response_model=SharedDesksWithTotal)
# async def get_shared_desks(
#     limit: int = Query(5, ge=0, le=100),
#     offset: int = Query(0, ge=0),
# ):
#     return SharedDesksWithTotal


# @router.get("/{desk_id}/shares", response_model=Shares)
# async def get_shares_of_desk():
#     return Shares


# @router.post("/{desk_id}/shares", response_model=Share)
# async def share_desk_with_user():
#     return Share


# @router.delete("/{desk_id}/shares/{user_id}", status_code=HTTPStatus.NO_CONTENT)
# async def revoke_desk_access(
#     desk_id: int,
#     user_id: int,
#     current_user: User = Depends(get_current_user)
# ):
#     return