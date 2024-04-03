from typing import Any, Annotated, List
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from ...core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from ...schemas.ride import RideRead, RideBase, RideCreate
from ...crud.crud_rides import crud_ride
from ...core.db.database import get_db_client
from bson import ObjectId
from datetime import datetime


router = APIRouter(prefix="/rides", tags=["rides"])

MONGO_COLLECTION_NAME = "rides"
MONGO_CLIENT = get_db_client()
mongo = MONGO_CLIENT[MONGO_COLLECTION_NAME]

PAGE_SIZE = 10


@router.post("/ride", status_code=status.HTTP_201_CREATED, response_model=RideRead)
async def get_ride(request: Request, user_ride: RideCreate):
    # db_user: RideRead | None = await crud_ride.get(
    #     db=db, schema_to_select=RideRead, username=username, is_deleted=False
    # )
    # if db_user is None:
    #     raise NotFoundException("User not found")
    ride_id = None
    try:
        user_ride = jsonable_encoder(user_ride)
        response = await mongo.insert_one(user_ride)

        if response is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create ride")

        ride_id = response.inserted_id
        print('id', response.inserted_id)

        created_ride = [await mongo.find_one({"_id": ObjectId(ride_id)})]

        if created_ride is None:
            # Delete the created ride
            await mongo.delete_one({"_id": ObjectId(ride_id)})
            # raise NotFoundException(
            #     "Failed to fetch created ride from database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

        for doc in created_ride:
            doc['_id'] = str(doc['_id'])

        return {
            'result': created_ride,
            'page': 1,
            'total': 1
        }

    except Exception as e:
        # Handle any unexpected exceptions
        if ride_id:
            await mongo.delete_one({"_id": ObjectId(ride_id)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


# get all rides

@router.get("", description="GET all rides paginated", response_model=RideRead)
async def get_ride(request: Request, page: int = 1):
    if page < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Page number must be greater than 0")

    skip = (page - 1) * PAGE_SIZE
    total = await mongo.count_documents({})

    if skip >= total:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Page number out of range")

    # Assuming 'date' is the field you want to sort by. Use -1 for descending order.
    response = await mongo.find().sort("date", -1).skip(skip).limit(PAGE_SIZE).to_list(length=None)

    if not response:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong")

    for doc in response:
        doc['_id'] = str(doc['_id'])

    return {
        'result': response,
        'page': page,
        'total': total
    }




# get ride with id


@router.get("/ride/{ride_id}", response_model=RideRead)
async def get_ride(request: Request, ride_id: str):
    if ride_id is None or (not ObjectId.is_valid(ride_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid ride id")

    response = [await mongo.find_one({"_id": ObjectId(ride_id)})]

    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Ride not found")
    for doc in response:
        doc['_id'] = str(doc['_id'])

    return {
        'result': response,
        'page': 1,
        'total': 1
    }


@router.get("/driver/{driver_user_id}", response_model=List[RideBase])
async def get_rides_for_driver(driver_user_id: str):
    now = datetime.now()
    rides = await mongo.find({
        "driverUserId": driver_user_id,
        "date": {"$gte": now.isoformat()}
    }).sort("date", 1).to_list(length=100)  # Adjust length as needed
    print(rides)
    for ride in rides:
        ride['_id'] = str(ride['_id'])

    return rides
