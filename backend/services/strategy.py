import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from loguru import logger

from backend.models.strategy import Strategy
from backend.schemas.strategy import StrategyCreate, StrategyUpdate
from backend.core.strategy.visual_builder.generator import CodeGenerator

class StrategyService:
    def __init__(self, db: Session):
        self.db = db

    async def get_strategies(self, skip: int = 0, limit: int = 100, category: Optional[str] = None) -> dict:
        """获取策略列表"""
        stmt = select(Strategy).order_by(Strategy.updated_at.desc())
        
        if category:
            stmt = stmt.where(Strategy.category == category)
            
        # Count total
        count_stmt = select(Strategy.id)
        if category:
            count_stmt = count_stmt.where(Strategy.category == category)
            
        total = len(self.db.execute(count_stmt).fetchall())
        
        # Paginate
        stmt = stmt.offset(skip).limit(limit)
        result = self.db.execute(stmt)
        strategies = result.scalars().all()
        
        return {
            "total": total,
            "items": strategies
        }

    async def get_strategy_by_id(self, strategy_id: uuid.UUID) -> Optional[Strategy]:
        """根据 ID 取单个策略信息"""
        stmt = select(Strategy).where(Strategy.id == strategy_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_strategy(self, data: StrategyCreate, user_id: uuid.UUID) -> Strategy:
        """创建策略"""
        try:
            strategy_dict = data.model_dump(exclude={"type"})
            strategy_dict["user_id"] = user_id
            
            # Type identifier mapping
            strategy_dict["is_visual"] = (data.type == "visual")
            
            new_strategy = Strategy(**strategy_dict)
            self.db.add(new_strategy)
            self.db.commit()
            self.db.refresh(new_strategy)
            
            logger.info(f"Created new strategy: {new_strategy.name} [{new_strategy.id}]")
            return new_strategy
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create strategy: {str(e)}")
            raise e

    async def update_strategy(self, strategy_id: uuid.UUID, data: StrategyUpdate) -> Optional[Strategy]:
        """更新策略（部分更新）"""
        try:
            strategy = await self.get_strategy_by_id(strategy_id)
            if not strategy:
                return None
                
            update_data = data.model_dump(exclude_unset=True)
            if not update_data:
                return strategy
                
            # Bump version if code has naturally changed
            if "code" in update_data and update_data["code"] != strategy.code:
                update_data["version"] = strategy.version + 1
                
            # React Flow Visual Builder Generate Code
            if "canvas_data" in update_data and update_data["canvas_data"]:
                generator = CodeGenerator(update_data["canvas_data"])
                generated_code = generator.generate()
                update_data["code"] = generated_code
                update_data["version"] = strategy.version + 1
                
            for key, value in update_data.items():
                setattr(strategy, key, value)
                
            self.db.commit()
            self.db.refresh(strategy)
            
            logger.info(f"Updated strategy: {strategy.name} [{strategy.id}]")
            return strategy
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update strategy {strategy_id}: {str(e)}")
            raise e

    async def delete_strategy(self, strategy_id: uuid.UUID) -> bool:
        """删除策略"""
        try:
            strategy = await self.get_strategy_by_id(strategy_id)
            if not strategy:
                return False
                
            self.db.delete(strategy)
            self.db.commit()
            
            logger.info(f"Deleted strategy: {strategy_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete strategy {strategy_id}: {str(e)}")
            raise e
