from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from model.session import Session


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID) -> Session:
        session = Session(user_id=user_id)
        self.session.add(session)
        await self.session.commit()
        await self.session.refresh(session)
        return session

    async def get_active_by_user(self, user_id: UUID) -> list[Session]:
        stmt = select(Session).where(
            Session.user_id == user_id,
            Session.is_active == True,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def deactivate(self, session_id: UUID) -> bool:
        stmt = (
            update(Session)
            .where(Session.id == session_id)
            .values(is_active=False, last_active=date.today())
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def delete_expired(self, before: date) -> int:
        stmt = delete(Session).where(Session.last_active < before)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount