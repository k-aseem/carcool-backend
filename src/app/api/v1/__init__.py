from fastapi import APIRouter

from .rides import router as rides_router

router = APIRouter(prefix="/v1")

router.include_router(rides_router)
