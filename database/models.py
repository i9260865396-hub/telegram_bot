from sqlalchemy import BigInteger, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database.db import Base

class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(4096), default="")
    status: Mapped[str] = mapped_column(String(64), default="new")
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
