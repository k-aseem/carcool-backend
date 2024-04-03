# schemas/booking.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .ride import RideBase  # Import the RideRead model

class BookingBase(BaseModel):
    userId: str
    rideId: str
    bookingDate: datetime
    status: str

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: str

class BookingRead(BookingBase):
    id: Optional[str] = None

# Extend BookingRead to include ride information
class BookingReadWithRide(BookingRead):
    ride: Optional[RideBase] = Field(None, description="The detailed information of the ride associated with this booking")
