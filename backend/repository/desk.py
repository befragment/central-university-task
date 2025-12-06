from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
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


class DeskDetailRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_or_update(
        self,
        desk_id: UUID,
        *,
        coord: str,
        size: str,
        color: str,
        text: str,
    ) -> DeskDetail:
        stmt = select(DeskDetail).where(DeskDetail.desk_id == desk_id)
        result = await self.session.execute(stmt)
        detail = result.scalar_one_or_none()

        if detail:
            detail.coord = coord
            detail.size = size
            detail.color = color
            detail.text = text
            detail.updated_at = date.today()
        else:
            detail = DeskDetail(
                desk_id=desk_id,
                coord=coord,
                size=size,
                color=color,
                text=text,
            )
            self.session.add(detail)

        await self.session.commit()
        await self.session.refresh(detail)
        return detail

    async def get_by_desk_id(self, desk_id: UUID) -> DeskDetail | None:
        stmt = select(DeskDetail).where(DeskDetail.desk_id == desk_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class DeskShareRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, desk_id: UUID, user_id: UUID) -> DeskShare:
        # Проверка дубликата не обязательна, но можно добавить unique constraint в БД
        share = DeskShare(desk_id=desk_id, user_id=user_id)
        self.session.add(share)
        await self.session.commit()
        await self.session.refresh(share)
        return share

    async def get_shared_desks_for_user(self, user_id: UUID) -> list[Desk]:
        stmt = (
            select(Desk)
            .join(DeskShare, Desk.id == DeskShare.desk_id)
            .where(DeskShare.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def remove(self, desk_id: UUID, user_id: UUID) -> bool:
        stmt = delete(DeskShare).where(
            DeskShare.desk_id == desk_id,
            DeskShare.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0