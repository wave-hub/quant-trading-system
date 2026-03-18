from fastapi import APIRouter
from backend.api.v1.backtest import routes

router = APIRouter()
router.include_router(routes.router, tags=["Backtest Tasks"])
