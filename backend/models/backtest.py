"""Backtest model."""

from sqlalchemy import Column, String, Text, Integer, Numeric, Date, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.config.database import Base
from backend.models.base import BaseModel


class BacktestTask(BaseModel, Base):
    """Backtest task model."""

    __tablename__ = "backtest_tasks"

    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False, index=True)
    name = Column(String(100))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_capital = Column(Numeric(20, 2), nullable=False)
    status = Column(String(20), default="pending", index=True)
    config = Column(JSON, default=dict)
    result = Column(JSON)
    error_message = Column(Text)
    progress = Column(Integer, default=0)

    strategy = relationship("Strategy", backref="backtest_tasks")

    def __repr__(self):
        return f"<BacktestTask(id={self.id}, name={self.name}, status={self.status})>"


class BacktestTrade(BaseModel, Base):
    """Backtest trade record model."""

    __tablename__ = "backtest_trades"

    backtest_id = Column(UUID(as_uuid=True), ForeignKey("backtest_tasks.id"), nullable=False, index=True)
    order_book_id = Column(String(50))
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(20, 4), nullable=False)
    commission = Column(Numeric(20, 4), default=0)
    trade_date = Column(Date, nullable=False)

    backtest_task = relationship("BacktestTask", backref="trades")

    def __repr__(self):
        return f"<BacktestTrade(id={self.id}, symbol={self.symbol}, side={self.side})>"
