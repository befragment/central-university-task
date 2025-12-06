from fastapi import APIRouter
from api.common import router as common_router
from api.auth import router as auth_router
from api.desk import router as desk_router
from api.user import router as user_router
from api.ws import router as ws_router  # добавить

api_router = APIRouter()

api_router.include_router(common_router)
api_router.include_router(auth_router)
api_router.include_router(desk_router)
api_router.include_router(user_router)
api_router.include_router(ws_router)