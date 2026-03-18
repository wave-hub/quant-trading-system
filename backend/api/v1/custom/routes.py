import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.services.custom import CustomComponentService
from backend.schemas.custom import (
    CustomIndicatorCreate, CustomIndicatorUpdate, CustomIndicatorResponse,
    CustomSignalCreate, CustomSignalUpdate, CustomSignalResponse,
    CustomPositionCreate, CustomPositionUpdate, CustomPositionResponse,
    CustomRiskRuleCreate, CustomRiskRuleUpdate, CustomRiskRuleResponse
)

router = APIRouter()

# Mock user for MVP
MOCK_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")

# ================= Indicators =================
@router.get("/indicators")
async def get_indicators(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    service = CustomComponentService(db)
    return await service.get_indicators(skip=skip, limit=limit, category=category)

@router.post("/indicators", response_model=CustomIndicatorResponse, status_code=201)
async def create_indicator(data: CustomIndicatorCreate, db: Session = Depends(get_db)):
    service = CustomComponentService(db)
    return await service.create_indicator(data, MOCK_USER_ID)

@router.put("/indicators/{item_id}", response_model=CustomIndicatorResponse)
async def update_indicator(item_id: uuid.UUID, data: CustomIndicatorUpdate, db: Session = Depends(get_db)):
    service = CustomComponentService(db)
    updated = await service.update_indicator(item_id, data)
    if not updated:
         raise HTTPException(status_code=404, detail="Indicator not found")
    return updated

@router.delete("/indicators/{item_id}", status_code=204)
async def delete_indicator(item_id: uuid.UUID, db: Session = Depends(get_db)):
    service = CustomComponentService(db)
    if not await service.delete_indicator(item_id):
        raise HTTPException(status_code=404, detail="Indicator not found")

# ================= Signals =================
@router.get("/signals")
async def get_signals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    service = CustomComponentService(db)
    return await service.get_signals(skip=skip, limit=limit, category=category)

@router.post("/signals", response_model=CustomSignalResponse, status_code=201)
async def create_signal(data: CustomSignalCreate, db: Session = Depends(get_db)):
    service = CustomComponentService(db)
    return await service.create_signal(data, MOCK_USER_ID)

@router.put("/signals/{item_id}", response_model=CustomSignalResponse)
async def update_signal(item_id: uuid.UUID, data: CustomSignalUpdate, db: Session = Depends(get_db)):
    service = CustomComponentService(db)
    updated = await service.update_signal(item_id, data)
    if not updated:
         raise HTTPException(status_code=404, detail="Signal not found")
    return updated

@router.delete("/signals/{item_id}", status_code=204)
async def delete_signal(item_id: uuid.UUID, db: Session = Depends(get_db)):
    service = CustomComponentService(db)
    if not await service.delete_signal(item_id):
        raise HTTPException(status_code=404, detail="Signal not found")

# ================= Positions =================
@router.get("/positions")
async def get_positions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    service = CustomComponentService(db)
    return await service.get_positions(skip=skip, limit=limit, category=category)

@router.post("/positions", response_model=CustomPositionResponse, status_code=201)
async def create_position(data: CustomPositionCreate, db: Session = Depends(get_db)):
    service = CustomComponentService(db)
    return await service.create_position(data, MOCK_USER_ID)

@router.put("/positions/{item_id}", response_model=CustomPositionResponse)
async def update_position(item_id: uuid.UUID, data: CustomPositionUpdate, db: Session = Depends(get_db)):
    service = CustomComponentService(db)
    updated = await service.update_position(item_id, data)
    if not updated:
         raise HTTPException(status_code=404, detail="Position rule not found")
    return updated

@router.delete("/positions/{item_id}", status_code=204)
async def delete_position(item_id: uuid.UUID, db: Session = Depends(get_db)):
    service = CustomComponentService(db)
    if not await service.delete_position(item_id):
        raise HTTPException(status_code=404, detail="Position rule not found")

# ================= Risk Rules =================
@router.get("/risk-rules")
async def get_risk_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    service = CustomComponentService(db)
    return await service.get_risk_rules(skip=skip, limit=limit, category=category)

@router.post("/risk-rules", response_model=CustomRiskRuleResponse, status_code=201)
async def create_risk_rule(data: CustomRiskRuleCreate, db: Session = Depends(get_db)):
    service = CustomComponentService(db)
    return await service.create_risk_rule(data, MOCK_USER_ID)

@router.put("/risk-rules/{item_id}", response_model=CustomRiskRuleResponse)
async def update_risk_rule(item_id: uuid.UUID, data: CustomRiskRuleUpdate, db: Session = Depends(get_db)):
    service = CustomComponentService(db)
    updated = await service.update_risk_rule(item_id, data)
    if not updated:
         raise HTTPException(status_code=404, detail="Risk rule not found")
    return updated

@router.delete("/risk-rules/{item_id}", status_code=204)
async def delete_risk_rule(item_id: uuid.UUID, db: Session = Depends(get_db)):
    service = CustomComponentService(db)
    if not await service.delete_risk_rule(item_id):
        raise HTTPException(status_code=404, detail="Risk rule not found")
