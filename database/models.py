from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, func, BigInteger
from database.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base

class Admin(Base):
    __tablename__ = "admins"

    user_id: Mapped[int] = mapped_column(primary_key=True)
# === Таблица заказов ===
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    description = Column(String(4096), nullable=False)
    status = Column(String(64), default="new")
    created_at = Column(DateTime, default=func.now())


# === Таблица услуг ===
class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)          # название услуги
    price = Column(Float, nullable=False, default=0)    # цена
    unit = Column(String(50), nullable=False, default="шт.")  # единица измерения (шт., м², м)
    min_qty = Column(Integer, nullable=False, default=1)      # минимальное количество
    is_active = Column(Boolean, default=True)           # доступность
