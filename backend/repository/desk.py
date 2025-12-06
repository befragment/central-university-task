from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.desk import Desk


class DeskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, desk_id: UUID) -> Desk | None:
        result = await self.session.execute(
            select(Desk).where(Desk.id == desk_id)
        )
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: UUID) -> list[Desk]:
        result = await self.session.execute(
            select(Desk).where(Desk.owner_id == owner_id)
        )
        return list(result.scalars().all())

    async def create(self, desk: Desk) -> Desk:
        self.session.add(desk)
        await self.session.commit()
        await self.session.refresh(desk)
        return desk

    async def update(self, desk: Desk) -> Desk:
        await self.session.commit()
        await self.session.refresh(desk)
        return desk

    async def delete(self, desk: Desk) -> None:
        await self.session.delete(desk)
        await self.session.commit()