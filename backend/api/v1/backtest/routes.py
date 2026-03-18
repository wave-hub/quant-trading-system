import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from loguru import logger

from backend.config.database import get_db
from backend.services.backtest import BacktestService
from backend.schemas.backtest import BacktestTaskCreate, BacktestTaskResponse, BacktestTaskWithTradesResponse
from backend.core.engine.simulator import FastSimulator

router = APIRouter()

def process_backtest_task(task_id: uuid.UUID):
    # This runs in background
    from backend.config.database import SessionLocal
    db = SessionLocal()
    try:
         simulator = FastSimulator(task_id, db)
         simulator.run()
    except Exception as e:
         logger.error(f"Simulator crashed for {task_id}: {str(e)}")
    finally:
         db.close()


@router.get("/", response_model=dict)
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = BacktestService(db)
    return await service.get_tasks(skip=skip, limit=limit)


@router.post("/", response_model=BacktestTaskResponse, status_code=201)
async def create_and_run_backtest(
    data: BacktestTaskCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    service = BacktestService(db)
    new_task = await service.create_task(data)
    
    # Fire and forget the simulator to avoid blocking the API
    background_tasks.add_task(process_backtest_task, new_task.id)
    
    return new_task

@router.get("/{task_id}", response_model=BacktestTaskWithTradesResponse)
async def get_task_detail(task_id: uuid.UUID, db: Session = Depends(get_db)):
    service = BacktestService(db)
    task = await service.get_task_by_id(task_id)
    if not task:
         raise HTTPException(status_code=404, detail="Task not found")
    return task
