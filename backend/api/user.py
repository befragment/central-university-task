from fastapi import APIRouter, Query, Depends

from api.dependencies import get_current_user
from api.dto import User, Users

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/search", response_model=Users)
async def search_users(
    q: str | None = Query(default=None),
):
    return {"users": []}