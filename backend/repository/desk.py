from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, exists
from model.desk import Desk, DeskDetail, DeskShare


class DeskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, owner_id: UUID) -> Desk:
        desk = Desk(name=name, owner_id=owner_id)
        self.session.add(desk)
        await self.session.commit()
        await self.session.refresh(desk)
        return desk

    async def get_by_id(self, desk_id: UUID) -> Desk | None:
        return await self.session.get(Desk, desk_id)

    async def get_owned_by_user(self, user_id: UUID) -> list[Desk]:
        stmt = select(Desk).where(Desk.owner_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars())
    
    async def is_owned_by_user(self, desk_id: UUID, user_id: UUID) -> bool:
        stmt = select(
            exists().where(
                Desk.id == desk_id,
                Desk.owner_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        return bool(result.scalar())


    async def update(self, desk_id: UUID, name: str | None = None) -> bool:
        values = {"updated_at": date.today()}
        if name is not None:
            values["name"] = name
        stmt = update(Desk).where(Desk.id == desk_id).values(**values)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def delete(self, desk_id: UUID) -> bool:
        stmt = delete(Desk).where(Desk.id == desk_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

