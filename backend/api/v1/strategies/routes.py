import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.services.strategy import StrategyService
from backend.schemas.strategy import StrategyCreate, StrategyUpdate, StrategyResponse, StrategyListResponse

router = APIRouter()

# Temporary mock user UUID until auth module is implemented
MOCK_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")

@router.get("/", response_model=StrategyListResponse)
async def get_strategies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取策略列表"""
    service = StrategyService(db)
    return await service.get_strategies(skip=skip, limit=limit, category=category)

@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: uuid.UUID, db: Session = Depends(get_db)):
    """获取某个具体的策略结构和代码详情"""
    service = StrategyService(db)
    strategy = await service.get_strategy_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(data: StrategyCreate, db: Session = Depends(get_db)):
    """新建一个策略片段（支持代码 / 可视化配置）"""
    service = StrategyService(db)
    return await service.create_strategy(data, user_id=MOCK_USER_ID)

@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: uuid.UUID, data: StrategyUpdate, db: Session = Depends(get_db)):
    """修改已有策略"""
    service = StrategyService(db)
    updated = await service.update_strategy(strategy_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return updated

@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(strategy_id: uuid.UUID, db: Session = Depends(get_db)):
    """删除指定策略"""
    service = StrategyService(db)
    deleted = await service.delete_strategy(strategy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Strategy not found")
