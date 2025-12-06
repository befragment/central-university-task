from fastapi import Depends 
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from repository import (
    DeskShareRepository,
    DeskDetailRepository,
    UserRepository, 
    DeskRepository
)

async def get_deskshare_repo(session: AsyncSession = Depends(get_db)):
    return DeskShareRepository(session)

async def get_deskdetail_repo(session: AsyncSession = Depends(get_db)):
    return DeskDetailRepository(session)

async def get_user_repo(session: AsyncSession = Depends(get_db)):
    return UserRepository(session)

async def get_desk_repo(session: AsyncSession = Depends(get_db)):
    return DeskRepository(session)
