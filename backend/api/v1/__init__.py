"""API v1 router."""

from fastapi import APIRouter

from backend.api.v1.factors.routes import router as factors_router
from backend.api.v1.factor_combination.routes import router as factor_combination_router
from backend.api.v1.risk.routes import router as risk_router
from backend.api.v1.data import router as data_router
from backend.api.v1.strategies import router as strategies_router
from backend.api.v1.custom import router as custom_router
from backend.api.v1.backtest import router as backtest_router
from backend.api.v1.trade import router as trade_router

router = APIRouter(prefix="/api/v1")
router.include_router(data_router, prefix="/data")
router.include_router(strategies_router, prefix="/strategies")
router.include_router(custom_router, prefix="/custom")
router.include_router(backtest_router, prefix="/backtest")
router.include_router(trade_router, prefix="/trade")
router.include_router(factors_router, prefix="/factors", tags=["factors"])
router.include_router(
    factor_combination_router, prefix="/factor-combination", tags=["factor-combination"]
)
router.include_router(risk_router, prefix="/risk", tags=["risk"])

__all__ = ["router"]

