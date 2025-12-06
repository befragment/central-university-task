from fastapi import APIRouter, Query, Depends

from api.dependencies import get_current_user
from api.dto import UserDTO, Users
from model import User
from api.dto import UserDTO, Users
from api.dependencies import get_user_repo, get_current_user
from repository.user import UserRepository

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserDTO)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/search", response_model=Users)
async def search_users(
    q: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    user_repo: UserRepository = Depends(get_user_repo),
):
    if not q or len(q.strip()) == 0:
        # Если q пустой — возвращаем всех пользователей
        users = await user_repo.get_all(limit=limit)
    else:
        users = await user_repo.search_by_email(q.strip(), limit=limit)

    return Users(
        users=[
            User(id=u.id, name=u.name, email=u.email)
            for u in users
        ]
    )






