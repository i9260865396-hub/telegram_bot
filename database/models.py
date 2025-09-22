from sqlalchemy import Column, Integer, BigInteger, String, DateTime, func
from database.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)        # Telegram ID пользователя
    description = Column(String(4096), nullable=False)  # описание заказа (например "100 листовок А6")
    status = Column(String(64), default="new")          # new / in_progress / done
    created_at = Column(DateTime(timezone=True), server_default=func.now())
