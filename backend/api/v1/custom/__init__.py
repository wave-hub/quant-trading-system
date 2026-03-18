from fastapi import APIRouter
from backend.api.v1.custom import routes

router = APIRouter()
router.include_router(routes.router, tags=["Custom Components"])
