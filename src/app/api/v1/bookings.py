# v1/bookings.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
from ...schemas.booking import BookingCreate, BookingRead, BookingUpdate, BookingReadWithRide
from fastapi.encoders import jsonable_encoder
from ...crud.crud_bookings import create_booking, update_booking
from ...core.db.database import get_db_client
from typing import List, Optional
from pymongo import DESCENDING
from bson import ObjectId


router = APIRouter(prefix="/bookings", tags=["bookings"])

from fastapi import HTTPException, status
from pymongo import ReturnDocument

@router.post("/", response_model=BookingRead)
async def create_or_update_booking(booking: BookingCreate):
    db = get_db_client()
    # Set the status to 'requested', no matter what the incoming status is
    booking_data = jsonable_encoder(booking)
    booking_data['status'] = 'requested'
    
    # Create a filter for a document with the matching userId and rideId
    filter_by = {'userId': booking_data['userId'], 'rideId': booking_data['rideId']}
    
    # Define the update to be performed - set the status to 'requested'
    update_data = {'$set': {'status': 'requested', 'bookingDate': booking_data['bookingDate']}}
    
    # Perform the upsert (update if exists, else insert)
    updated_booking = await db["booking"].find_one_and_update(
        filter_by, update_data, upsert=True, return_document=ReturnDocument.AFTER
    )
    
    # If the operation did not succeed, raise an HTTPException
    if not updated_booking:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create or update booking"
        )

    # Convert the MongoDB's _id field to a string id in the response
    updated_booking['id'] = str(updated_booking.pop('_id'))
    booking_dict = jsonable_encoder(updated_booking)
    #del booking_dict["_id"]  # Delete the original _id from the response
    
    return booking_dict


@router.put("/{booking_id}", response_model=BookingRead)
async def update_a_booking(booking_id: str, booking: BookingUpdate):
    print(booking_id)
    print(BookingUpdate)
    db = get_db_client()
    updated_booking = await update_booking(db, booking_id, booking)
    if not updated_booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return updated_booking


@router.post("/check-status", response_model=Optional[BookingRead])
async def check_booking_status(userId: str = Body(...), rideId: str = Body(...)):
    db = get_db_client()
    booking_document = await db["booking"].find_one({"userId": userId, "rideId": rideId},  sort=[("bookingDate", DESCENDING)])
    
    if booking_document:
        # Convert the _id field from ObjectId to a string and rename it to id
        booking_document['id'] = str(booking_document.pop('_id'))
        # Use jsonable_encoder to handle types like ObjectId
        booking = jsonable_encoder(booking_document)
        return booking

    return None


@router.get("/for-ride/{ride_id}", response_model=List[Optional[BookingRead]])
async def get_bookings_for_ride(ride_id: str):
    db = get_db_client()
    bookings_documents = await db["booking"].find(
        {"rideId": ride_id}
    ).sort("bookingDate", DESCENDING).to_list(length=None)  # Adjust length as needed
    
    # Convert the _id field from ObjectId to a string for each booking document
    for booking_document in bookings_documents:
        booking_document['id'] = str(booking_document.pop('_id'))
    
    bookings = [jsonable_encoder(booking_document) for booking_document in bookings_documents]
    print(bookings)
    print("xx")
    return bookings

@router.get("/for-user/{user_id}")
async def get_bookings_for_user(user_id: str):
    db = get_db_client()
    bookings_documents = await db["booking"].find(
        {"userId": user_id}
    ).sort("bookingDate", DESCENDING).to_list(length=None)

    # Prepare a list to hold bookings with appended ride information
    bookings_with_rides = []

    for booking_document in bookings_documents:
        # Fetch the corresponding ride for each booking using rideId
        ride_document = await db["rides"].find_one({"_id": ObjectId(booking_document["rideId"])})
        
        # Convert ObjectId to string in ride document if needed
        print(booking_document["rideId"]);
        if ride_document:
            ride_document['id'] = str(ride_document.pop('_id'))
            # Append ride information to the booking document
            booking_document['ride'] = ride_document
            
            # Convert the _id field in the booking document from ObjectId to a string
            booking_document['id'] = str(booking_document.pop('_id'))
            
            # Add the modified booking document to the list
            bookings_with_rides.append(jsonable_encoder(booking_document))
    print(bookings_with_rides)
    return bookings_with_rides
