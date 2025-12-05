from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from .session import Session
    from .desk import Desk, DeskShare



class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    pass_hash: Mapped[str] = mapped_column(String, nullable=False)

    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
    desks_owned: Mapped[list["Desk"]] = relationship(back_populates="owner")
    desk_shares: Mapped[list["DeskShare"]] = relationship(back_populates="user")