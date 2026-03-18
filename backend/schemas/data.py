from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field

class StockBase(BaseModel):
    symbol: str = Field(..., description="股票代码, 如 000001.SZ")
    name: str = Field(..., description="股票名称")
    market: str = Field(..., description="所属市场")
    industry: Optional[str] = Field(None, description="所属行业")
    list_date: Optional[date] = Field(None, description="上市日期")
    is_hs: Optional[str] = Field(None, description="是否沪深港通标的")

class StockResponse(StockBase):
    id: str
    class Config:
        from_attributes = True

class StockListResponse(BaseModel):
    total: int
    items: List[StockResponse]

class MarketDataBase(BaseModel):
    symbol: str
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float
    adj_close: Optional[float] = None

class MarketDataResponse(MarketDataBase):
    id: str
    class Config:
        from_attributes = True

class MarketDataListResponse(BaseModel):
    total: int
    items: List[MarketDataResponse]
