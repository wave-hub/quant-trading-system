import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from loguru import logger

from backend.config.database import get_db
from backend.services.trade import TradeService
from backend.schemas.trade import (
    AccountResponse, AccountCreate, AccountWithDetailsResponse,
    PositionResponse, OrderResponse, OrderCreate,
    FundRequest, FundResponse
)

router = APIRouter()

# Mock user for MVP
MOCK_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")

# ==================== Accounts ====================
@router.get("/accounts", response_model=List[AccountResponse])
async def get_accounts(db: Session = Depends(get_db)):
    service = TradeService(db)
    
    # 强制让每个使用此接口的用户都有一个保底模拟盘
    await service.get_or_create_default_simulation_account(MOCK_USER_ID)
    
    accounts = await service.get_accounts(MOCK_USER_ID)
    return accounts

@router.get("/accounts/{account_id}/summary", response_model=AccountWithDetailsResponse)
async def get_account_summary(account_id: uuid.UUID, db: Session = Depends(get_db)):
    service = TradeService(db)
    account = await service.get_account_by_id(account_id)
    if not account or account.user_id != MOCK_USER_ID:
        raise HTTPException(status_code=404, detail="Account not found")
        
    positions = await service.get_positions(account_id)
    orders = await service.get_orders(account_id, limit=20)
    
    response = AccountWithDetailsResponse.model_validate(account)
    response.positions = positions
    response.orders = orders
    return response

@router.post("/accounts/{account_id}/fund", response_model=FundResponse)
async def fund_account(
    account_id: uuid.UUID,
    data: FundRequest,
    db: Session = Depends(get_db)
):
    """资金划拨接口：充值(deposit)或提现(withdraw)"""
    service = TradeService(db)
    try:
        result = await service.fund_account(account_id, data.action, data.amount)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"资金划拨失败: {e}")
        raise HTTPException(status_code=500, detail="资金划拨操作异常")

# ==================== Positions ====================
@router.get("/positions/{account_id}", response_model=List[PositionResponse])
async def get_positions(account_id: uuid.UUID, db: Session = Depends(get_db)):
    service = TradeService(db)
    return await service.get_positions(account_id)

# ==================== Orders ====================
@router.get("/orders/{account_id}", response_model=List[OrderResponse])
async def get_orders(account_id: uuid.UUID, limit: int = 50, db: Session = Depends(get_db)):
    service = TradeService(db)
    return await service.get_orders(account_id, limit)

@router.post("/orders", response_model=OrderResponse, status_code=201)
async def place_order(data: OrderCreate, db: Session = Depends(get_db)):
    service = TradeService(db)
    try:
        new_order = await service.place_order(data)
        return new_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to place order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error parsing order")
