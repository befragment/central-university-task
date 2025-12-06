from fastapi import APIRouter, Query

from api.dto import User, Users

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
async def get_me():
    return User


@router.get("/search", response_model=Users)
async def search_users(
    q: str | None = Query(default=None),
):
    return {"users": []}