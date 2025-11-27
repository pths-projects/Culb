from sqlalchemy import ForeignKey, String, Text, Boolean, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from utils.databases import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(Text)
    interests: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Отношения
    owned_clubs: Mapped[list["Club"]] = relationship("Club", back_populates="owner", foreign_keys="Club.owner_id")
    memberships: Mapped[list["Member"]] = relationship("Member", back_populates="user")

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id!r}, name={self.name!r}, username={self.username!r})"


class Club(Base):
    __tablename__ = "clubs"

    club_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)
    chat_link: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Отношения
    owner: Mapped["User"] = relationship("User", back_populates="owned_clubs", foreign_keys=[owner_id])
    members: Mapped[list["Member"]] = relationship("Member", back_populates="club")

    def __repr__(self) -> str:
        return f"Club(club_id={self.club_id!r}, name={self.name!r}, owner_id={self.owner_id!r})"


class Member(Base):
    __tablename__ = "members"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), primary_key=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.club_id"), primary_key=True)
    joined_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="memberships")
    club: Mapped["Club"] = relationship("Club", back_populates="members")

    def __repr__(self) -> str:
        return f"Member(user_id={self.user_id!r}, club_id={self.club_id!r})"