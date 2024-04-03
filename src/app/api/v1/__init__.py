from fastapi import APIRouter

from .rides import router as rides_router
from .bookings import router as bookings_router

router = APIRouter(prefix="/v1")

router.include_router(rides_router)
router.include_router(bookings_router)
