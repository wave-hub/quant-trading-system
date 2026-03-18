"""Data API router."""

from fastapi import APIRouter
from backend.api.v1.data.market import router as market_router

router = APIRouter()
router.include_router(market_router, prefix="/market", tags=["market-data"])

__all__ = ["router"]
