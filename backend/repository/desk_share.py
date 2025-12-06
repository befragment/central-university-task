from uuid import UUID
from sqlalchemy import select, and_, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from model import User

from model.desk import Desk, DeskShare


class DeskShareRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def has_access(self, user_id: UUID, desk_id: UUID) -> bool:
        """Check if user is owner or has share access."""
        # Check if owner
        desk_result = await self.session.execute(
            select(Desk).where(
                and_(Desk.id == desk_id, Desk.owner_id == user_id)
            )
        )
        if desk_result.scalar_one_or_none():
            return True

        # Check if shared
        share_result = await self.session.execute(
            select(DeskShare).where(
                and_(DeskShare.desk_id == desk_id, DeskShare.user_id == user_id)
            )
        )
        return share_result.scalar_one_or_none() is not None

    async def get_by_desk_id(self, desk_id: UUID) -> list[DeskShare]:
        result = await self.session.execute(
            select(DeskShare).where(DeskShare.desk_id == desk_id)
        )
        return list(result.scalars().all())

    async def get_shared_desks(self, user_id: UUID) -> list[DeskShare]:
        result = await self.session.execute(
            select(DeskShare).where(DeskShare.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(self, share: DeskShare) -> DeskShare:
        self.session.add(share)
        await self.session.commit()
        await self.session.refresh(share)
        return share

    async def delete(self, share: DeskShare) -> None:
        await self.session.delete(share)
        await self.session.commit()

    async def find(self, desk_id: UUID, user_id: UUID) -> DeskShare | None:
        result = await self.session.execute(
            select(DeskShare).where(
                and_(DeskShare.desk_id == desk_id, DeskShare.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()
    
    async def delete_user_from_desk_share(self, desk_id: UUID, user_id: UUID) -> int:
        stmt = (
            delete(DeskShare)
            .where(
                DeskShare.desk_id == desk_id,
                DeskShare.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount or 0
    
    async def add_user_to_desk_share(self, desk_id: UUID, user_id: UUID) -> DeskShare:
        # проверить дубль
        stmt = select(DeskShare).where(
            DeskShare.desk_id == desk_id,
            DeskShare.user_id == user_id,
        )
        res = await self.session.execute(stmt)
        existing = res.scalars().first()
        if existing:
            # eager подгрузка
            stmt2 = (
                select(DeskShare)
                .where(DeskShare.id == existing.id)
                .options(selectinload(DeskShare.user))
            )
            res2 = await self.session.execute(stmt2)
            return res2.scalars().one()

        share = DeskShare(desk_id=desk_id, user_id=user_id)
        self.session.add(share)
        await self.session.commit()
        await self.session.refresh(share)

        stmt3 = (
            select(DeskShare)
            .where(DeskShare.id == share.id)
            .options(selectinload(DeskShare.user))
        )
        res3 = await self.session.execute(stmt3)
        return res3.scalars().one()
    
    async def get_shares_with_users(self, desk_id: UUID) -> list[DeskShare]:
        stmt = (
            select(DeskShare)
            .where(DeskShare.desk_id == desk_id)
            .options(selectinload(DeskShare.user))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())