"""Account, Position and Order models."""

from sqlalchemy import Column, String, Numeric, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.config.database import Base
from backend.models.base import BaseModel


class Account(BaseModel, Base):
    """Account model."""

    __tablename__ = "accounts"

    name = Column(String(100), nullable=False)
    account_type = Column(String(20), nullable=False)
    broker = Column(String(50))
    account_number = Column(String(50))
    initial_capital = Column(Numeric(20, 2), nullable=False)
    current_capital = Column(Numeric(20, 2), nullable=False)
    status = Column(String(20), default="active")
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    positions = relationship("Position", back_populates="account", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Account(id={self.id}, name={self.name}, type={self.account_type})>"


class Position(BaseModel, Base):
    """Position model."""

    __tablename__ = "positions"

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    avg_price = Column(Numeric(20, 4))
    market_price = Column(Numeric(20, 4))
    market_value = Column(Numeric(20, 2))
    profit_loss = Column(Numeric(20, 2))

    account = relationship("Account", back_populates="positions")

    def __repr__(self):
        return f"<Position(id={self.id}, symbol={self.symbol}, quantity={self.quantity})>"


class Order(BaseModel, Base):
    """Order model."""

    __tablename__ = "orders"

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, index=True)
    order_id = Column(String(50), unique=True, index=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    order_type = Column(String(20), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(20, 4))
    status = Column(String(20), default="pending", index=True)
    filled_quantity = Column(Integer, default=0)
    avg_fill_price = Column(Numeric(20, 4))

    account = relationship("Account", back_populates="orders")

    def __repr__(self):
        return f"<Order(id={self.id}, symbol={self.symbol}, side={self.side}, status={self.status})>"
