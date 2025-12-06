from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from model.desk import DeskDetail


class DeskDetailRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_desk_id(self, desk_id: UUID) -> list[DeskDetail]:
        result = await self.session.execute(
            select(DeskDetail).where(DeskDetail.desk_id == desk_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, sticker_id: UUID) -> DeskDetail | None:
        result = await self.session.execute(
            select(DeskDetail).where(DeskDetail.id == sticker_id)
        )
        return result.scalar_one_or_none()

    async def create(self, sticker: DeskDetail) -> DeskDetail:
        self.session.add(sticker)
        await self.session.commit()
        await self.session.refresh(sticker)
        return sticker

    async def update(self, sticker: DeskDetail) -> DeskDetail:
        await self.session.commit()
        await self.session.refresh(sticker)
        return sticker

    async def delete(self, sticker: DeskDetail) -> None:
        await self.session.delete(sticker)
        await self.session.commit()

    async def delete_by_desk_id(self, desk_id: UUID) -> None:
        await self.session.execute(
            delete(DeskDetail).where(DeskDetail.desk_id == desk_id)
        )
        await self.session.commit()