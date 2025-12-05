from fastapi import APIRouter

from api.dto import (
    DeskCreateRequest, 
    DeskCreateResponse, 
    DeskDeleteRequest, 
    DeskDeleteResponse, 
    DeskUpdateRequest,
    DeskUpdateResponse,
)

router = APIRouter(prefix="/desk", tags=["desk"])

@router.post("/create", response_model=DeskCreateResponse)
async def create_desk(
    request: DeskCreateRequest,
):
    return DeskCreateResponse


@router.delete("/delete", response_model=DeskDeleteResponse)
async def delete_desk(
    request: DeskDeleteRequest
):
    return DeskDeleteResponse


@router.patch("/update", response_model=DeskUpdateResponse)
async def delete_desk(
    request: DeskUpdateRequest
):
    return DeskUpdateResponse