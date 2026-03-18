from fastapi import APIRouter
from backend.api.v1.trade import routes

router = APIRouter()
router.include_router(routes.router, tags=["Live Trading"])
