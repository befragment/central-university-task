from fastapi import APIRouter, Query

from api.dto import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
async def get_me():
    return User


@router.get("/search")
async def search_users(
    q: str | None = Query(default=None),
):
    return {"users": []}