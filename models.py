from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, PickleType
from typing import List


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    userid: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=True)
    buff_watchlist = Column(PickleType)
    buff_investments = Column(PickleType)
    stock_watchlist = Column(PickleType)
    stock_investments = Column(PickleType)
