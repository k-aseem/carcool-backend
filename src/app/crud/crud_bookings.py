# crud/crud_bookings.py

from bson import ObjectId
from ..schemas.booking import BookingCreate, BookingUpdate

async def create_booking(db, booking: BookingCreate):
    booking = await db["booking"].insert_one(booking.dict())
    return booking

async def update_booking(db, booking_id: str, booking: BookingUpdate):
    await db["booking"].update_one(
        {"_id": ObjectId(booking_id)}, {"$set": booking.dict()}
    )
    return await db["booking"].find_one({"_id": ObjectId(booking_id)})
