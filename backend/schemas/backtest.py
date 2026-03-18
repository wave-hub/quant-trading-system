import uuid
from typing import Dict, Any, Optional, List
from datetime import date
from pydantic import BaseModel, Field

# ========= Backtest Trade =========

class BacktestTradeBase(BaseModel):
    order_book_id: Optional[str] = None
    symbol: str
    side: str
    quantity: int
    price: float
    commission: float = 0.0
    trade_date: date

class BacktestTradeResponse(BacktestTradeBase):
    id: uuid.UUID
    backtest_id: uuid.UUID
    
    model_config = {"from_attributes": True}


# ========= Backtest Task =========

class BacktestTaskBase(BaseModel):
    strategy_id: uuid.UUID
    name: str = Field(..., max_length=100)
    start_date: date
    end_date: date
    initial_capital: float = Field(..., gt=0)
    config: Dict[str, Any] = Field(default_factory=dict)

class BacktestTaskCreate(BacktestTaskBase):
    pass

class BacktestTaskUpdate(BaseModel):
    status: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: Optional[int] = None

class BacktestTaskResponse(BacktestTaskBase):
    id: uuid.UUID
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: int
    created_at: Optional[Any] = None

    model_config = {"from_attributes": True}

class BacktestTaskWithTradesResponse(BacktestTaskResponse):
    trades: List[BacktestTradeResponse] = []
