from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from .user import User


class Desk(Base):
    __tablename__ = "desks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(String, nullable=False)

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=False,
    )

    created_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    updated_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    owner: Mapped["User"] = relationship(back_populates="desks_owned")
    details: Mapped[list["DeskDetail"]] = relationship(back_populates="desk")
    shares: Mapped[list["DeskShare"]] = relationship(back_populates="desk")


class DeskDetail(Base):
    __tablename__ = "desk_detail"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    created_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    updated_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    desk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("desks.id"),
        nullable=False,
    )

    coord: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)

    desk: Mapped["Desk"] = relationship(back_populates="details")


class DeskShare(Base):
    __tablename__ = "desk_share"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    desk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("desks.id"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=False,
    )

    created_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    desk: Mapped["Desk"] = relationship(back_populates="shares")
    user: Mapped["User"] = relationship(back_populates="desk_shares")