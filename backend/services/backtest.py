import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from loguru import logger

from backend.models.backtest import BacktestTask, BacktestTrade
from backend.schemas.backtest import BacktestTaskCreate, BacktestTaskUpdate

class BacktestService:
    def __init__(self, db: Session):
        self.db = db

    async def get_tasks(self, skip: int = 0, limit: int = 100) -> dict:
        """获取回测任务列表"""
        stmt = select(BacktestTask).order_by(BacktestTask.created_at.desc())
        count_stmt = select(BacktestTask.id)
        
        total = len(self.db.execute(count_stmt).fetchall())
        stmt = stmt.offset(skip).limit(limit)
        items = self.db.execute(stmt).scalars().all()
        
        return {"total": total, "items": items}

    async def get_task_by_id(self, task_id: uuid.UUID) -> Optional[BacktestTask]:
        """获取单个回测详情含交易记录"""
        stmt = select(BacktestTask).where(BacktestTask.id == task_id)
        return self.db.execute(stmt).scalar_one_or_none()

    async def create_task(self, data: BacktestTaskCreate) -> BacktestTask:
        """创建回测任务（初始状态 pending）"""
        try:
            task_dict = data.model_dump()
            task_dict["status"] = "pending"
            task_dict["progress"] = 0
            
            new_task = BacktestTask(**task_dict)
            self.db.add(new_task)
            self.db.commit()
            self.db.refresh(new_task)
            
            logger.info(f"Created new backtest task: {new_task.name} [{new_task.id}]")
            return new_task
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create backtest task: {str(e)}")
            raise e

    async def update_task_status(self, task_id: uuid.UUID, data: BacktestTaskUpdate) -> Optional[BacktestTask]:
        """更新任务状态及图表结果"""
        try:
            task = await self.get_task_by_id(task_id)
            if not task:
                return None
                
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(task, key, value)
                
            self.db.commit()
            self.db.refresh(task)
            return task
        except Exception as e:
            self.db.rollback()
            raise e
