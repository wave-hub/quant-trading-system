from typing import Any
import uuid
from typing import List, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy import select
from loguru import logger

from backend.models.custom import CustomIndicator, CustomSignal, CustomPosition, CustomRiskRule
from backend.schemas.custom import (
    CustomIndicatorCreate, CustomIndicatorUpdate,
    CustomSignalCreate, CustomSignalUpdate,
    CustomPositionCreate, CustomPositionUpdate,
    CustomRiskRuleCreate, CustomRiskRuleUpdate
)

class CustomComponentService:
    def __init__(self, db: Session):
        self.db = db

    # Helper method for generic CRUD
    async def _get_list(self, model: Type, skip: int = 0, limit: int = 100, category: Optional[str] = None) -> dict:
        stmt = select(model).order_by(model.updated_at.desc())
        if category:
            stmt = stmt.where(model.category == category)
            
        count_stmt = select(model.id)
        if category:
            count_stmt = count_stmt.where(model.category == category)
            
        total = len(self.db.execute(count_stmt).fetchall())
        stmt = stmt.offset(skip).limit(limit)
        items = self.db.execute(stmt).scalars().all()
        
        return {"total": total, "items": items}

    async def _get_by_id(self, model: Type, item_id: uuid.UUID):
        return self.db.execute(select(model).where(model.id == item_id)).scalar_one_or_none()

    async def _create(self, model: Type, data: Any, user_id: uuid.UUID):
        try:
            item_dict = data.model_dump()
            item_dict["author_id"] = user_id
            
            new_item = model(**item_dict)
            self.db.add(new_item)
            self.db.commit()
            self.db.refresh(new_item)
            
            logger.info(f"Created new {model.__name__}: {new_item.name}")
            return new_item
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create {model.__name__}: {str(e)}")
            raise e

    async def _update(self, model: Type, item_id: uuid.UUID, data: Any):
        try:
            item = await self._get_by_id(model, item_id)
            if not item:
                return None
                
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(item, key, value)
                
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception as e:
            self.db.rollback()
            raise e

    async def _delete(self, model: Type, item_id: uuid.UUID) -> bool:
        try:
             item = await self._get_by_id(model, item_id)
             if not item:
                 return False
                 
             self.db.delete(item)
             self.db.commit()
             return True
        except Exception as e:
             self.db.rollback()
             raise e

    # ============== Custom Indicators ==============
    async def get_indicators(self, skip: int = 0, limit: int = 100, category: str = None):
        return await self._get_list(CustomIndicator, skip, limit, category)

    async def get_indicator_by_id(self, item_id: uuid.UUID):
        return await self._get_by_id(CustomIndicator, item_id)

    async def create_indicator(self, data: CustomIndicatorCreate, user_id: uuid.UUID):
        return await self._create(CustomIndicator, data, user_id)

    async def update_indicator(self, item_id: uuid.UUID, data: CustomIndicatorUpdate):
        return await self._update(CustomIndicator, item_id, data)

    async def delete_indicator(self, item_id: uuid.UUID):
        return await self._delete(CustomIndicator, item_id)
        
    # ============== Custom Signals ==============
    async def get_signals(self, skip: int = 0, limit: int = 100, category: str = None):
        return await self._get_list(CustomSignal, skip, limit, category)

    async def get_signal_by_id(self, item_id: uuid.UUID):
        return await self._get_by_id(CustomSignal, item_id)

    async def create_signal(self, data: CustomSignalCreate, user_id: uuid.UUID):
        return await self._create(CustomSignal, data, user_id)

    async def update_signal(self, item_id: uuid.UUID, data: CustomSignalUpdate):
        return await self._update(CustomSignal, item_id, data)

    async def delete_signal(self, item_id: uuid.UUID):
        return await self._delete(CustomSignal, item_id)

    # ============== Custom Positions ==============
    async def get_positions(self, skip: int = 0, limit: int = 100, category: str = None):
        return await self._get_list(CustomPosition, skip, limit, category)

    async def get_position_by_id(self, item_id: uuid.UUID):
        return await self._get_by_id(CustomPosition, item_id)

    async def create_position(self, data: CustomPositionCreate, user_id: uuid.UUID):
        return await self._create(CustomPosition, data, user_id)

    async def update_position(self, item_id: uuid.UUID, data: CustomPositionUpdate):
        return await self._update(CustomPosition, item_id, data)

    async def delete_position(self, item_id: uuid.UUID):
        return await self._delete(CustomPosition, item_id)

    # ============== Custom Risk Rules ==============
    async def get_risk_rules(self, skip: int = 0, limit: int = 100, category: str = None):
        return await self._get_list(CustomRiskRule, skip, limit, category)

    async def get_risk_rule_by_id(self, item_id: uuid.UUID):
        return await self._get_by_id(CustomRiskRule, item_id)

    async def create_risk_rule(self, data: CustomRiskRuleCreate, user_id: uuid.UUID):
        return await self._create(CustomRiskRule, data, user_id)

    async def update_risk_rule(self, item_id: uuid.UUID, data: CustomRiskRuleUpdate):
        return await self._update(CustomRiskRule, item_id, data)

    async def delete_risk_rule(self, item_id: uuid.UUID):
        return await self._delete(CustomRiskRule, item_id)
