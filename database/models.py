# database/models.py
from sqlalchemy import Column, Integer, String, DateTime, func
from database.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)          # ID пользователя (из Telegram)
    description = Column(String, nullable=False)       # описание заказа (например "100 листовок А6")
    status = Column(String, default="new")             # new / in_progress / done
    created_at = Column(DateTime(timezone=True), server_default=func.now())
