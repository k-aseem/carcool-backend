from typing import Any, Annotated
from fastapi import APIRouter, Depends, Request
from ...core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from ...schemas.ride import RideRead
from ...crud.crud_rides import crud_ride

router = APIRouter(prefix="/rides", tags=["rides"])


# @router.post("/task", response_model=Job, status_code=201, dependencies=[Depends(rate_limiter)])
# async def create_task(message: str) -> dict[str, str]:
#     """Create a new background task.

#     Parameters
#     ----------
#     message: str
#         The message or data to be processed by the task.

#     Returns
#     -------
#     dict[str, str]
#         A dictionary containing the ID of the created task.
#     """
#     job = await queue.pool.enqueue_job("sample_background_task", message)  # type: ignore
#     return {"id": job.job_id}


sample_ride = {
    # Assuming a string representation for ObjectId
    "id": "63f5f54a25f54c5654a254a2",
    "driverId": "63f5f54a25f54c4a25f54a25",
    "startLocation": "123 Main Street, Anytown",
    "startLocationCoordinates": "40.7128, -74.0060",
    "destination": "XYZ Airport",
    "destinationCoordinates": "40.6442, -73.7822",
    "stopPoints": ["567 Elm Street, Anytown", "ABC Park"],
    "date": "2024-02-20",  # ISO 8601 format for datetime
    "time": "10:30 AM",
    "availableSeats": 3,
    "tentativePrice": 25.50,
    "carMake": "Toyota",
    "carModel": "Camry",
    "carYear": 2020,
    "carColor": "Silver",
    "carPlateNumber": "ABC123",
    "createdAt": "2024-02-15T16:45:00",  # ISO 8601 format
    "updatedAt": "2024-02-19T10:00:00",
    "bookings": None,  # No bookings yet
    "status": "OPEN"  # Enum value for status
}


@router.get("/ride/{ride_id}", response_model=RideRead)
async def get_ride(request: Request, ride_id: str) -> dict:
    # db_user: RideRead | None = await crud_ride.get(
    #     db=db, schema_to_select=RideRead, username=username, is_deleted=False
    # )
    # if db_user is None:
    #     raise NotFoundException("User not found")

    return sample_ride
