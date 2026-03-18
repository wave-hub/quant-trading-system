"""Strategies API router."""

from fastapi import APIRouter
from backend.api.v1.strategies.routes import router as strategy_routes

router = APIRouter()
router.include_router(strategy_routes, tags=["strategies"])

__all__ = ["router"]
