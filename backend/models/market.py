"""Market data model."""

from sqlalchemy import Column, String, Numeric, BigInteger, Date
from sqlalchemy.dialects.postgresql import UUID

from backend.config.database import Base
from backend.models.base import BaseModel


class MarketData(BaseModel, Base):
    """Market data model."""

    __tablename__ = "market_data"

    symbol = Column(String(20), nullable=False, index=True)
    trade_date = Column(Date, nullable=False)
    open = Column(Numeric(20, 4))
    high = Column(Numeric(20, 4))
    low = Column(Numeric(20, 4))
    close = Column(Numeric(20, 4))
    volume = Column(BigInteger)
    amount = Column(Numeric(20, 2))
    adj_close = Column(Numeric(20, 4))

    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )

    def __repr__(self):
        return f"<MarketData(symbol={self.symbol}, date={self.trade_date})>"


class Stock(BaseModel, Base):
    """Stock basic info model."""

    __tablename__ = "stocks"

    symbol = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    market = Column(String(20), nullable=False)
    industry = Column(String(50))
    list_date = Column(Date)
    is_hs = Column(String(10))

    def __repr__(self):
        return f"<Stock(symbol={self.symbol}, name={self.name})>"
