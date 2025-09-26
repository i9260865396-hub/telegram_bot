from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from datetime import datetime

class Base(DeclarativeBase):
    pass

# ------------------------
#   Заказы
# ------------------------
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# ------------------------
#   Услуги
# ------------------------
class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str] = mapped_column(String(20), default="шт.")
    min_qty: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

# ------------------------
#   Админы
# ------------------------
class Admin(Base):
    __tablename__ = "admins"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)

# ------------------------
#   Настройки (key-value)
# ------------------------
class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[str] = mapped_column(String(200))

    def __repr__(self):
        return f"<Setting {self.key}={self.value}>"

class Settings(BaseSettings):
    AI_ENABLED: bool = False
    NOTIFY_ENABLED: bool = True
    WORKDAY_END_HOUR: int = 16
    TIMEZONE: str = "Europe/Vilnius"
