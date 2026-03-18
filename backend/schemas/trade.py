import uuid
from typing import Optional, List
from pydantic import BaseModel, Field

# ==================== Account ====================
class AccountBase(BaseModel):
    name: str = Field(..., max_length=100)
    account_type: str = Field(..., max_length=20)   # 'simulation' 模拟 or 'real' 实盘
    broker: Optional[str] = None
    account_number: Optional[str] = None
    initial_capital: float = Field(..., ge=0)
    current_capital: float = Field(..., ge=0)
    status: str = "active"

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    id: uuid.UUID
    user_id: uuid.UUID
    
    model_config = {"from_attributes": True}

# ==================== Position ====================
class PositionBase(BaseModel):
    account_id: uuid.UUID
    symbol: str
    quantity: int
    avg_price: Optional[float] = None
    market_price: Optional[float] = None
    market_value: Optional[float] = None
    profit_loss: Optional[float] = None

class PositionResponse(PositionBase):
    id: uuid.UUID
    model_config = {"from_attributes": True}


# ==================== Order ====================
class OrderBase(BaseModel):
    account_id: uuid.UUID
    symbol: str
    side: str            # 'buy', 'sell'
    order_type: str      # 'market', 'limit'
    quantity: int = Field(..., gt=0)
    price: Optional[float] = None  # None usually means market order
    
class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: uuid.UUID
    order_id: str
    status: str          # 'pending', 'filled', 'cancelled'
    filled_quantity: int
    avg_fill_price: Optional[float] = None
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


# ==================== Account Aggregate ====================
class AccountWithDetailsResponse(AccountResponse):
    positions: List[PositionResponse] = []
    orders: List[OrderResponse] = []


# ==================== Fund (资金划拨) ====================
class FundRequest(BaseModel):
    """资金划拨请求：入金(deposit) 或 出金(withdraw)"""
    action: str = Field(..., pattern="^(deposit|withdraw)$", description="操作类型: deposit / withdraw")
    amount: float = Field(..., gt=0, description="金额，必须大于0")

class FundResponse(BaseModel):
    """资金划拨结果"""
    message: str
    action: str
    amount: float
    balance_before: float
    balance_after: float
