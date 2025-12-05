from fastapi import APIRouter
from api.common import router as common_router 

api_router = APIRouter()
api_router.include_router(common_router)
