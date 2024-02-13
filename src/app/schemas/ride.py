from datetime import datetime
from enum import Enum
from typing import Annotated, Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field, validator


class RideBase(BaseModel):
    id: str = Field(...)


class RideStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class RideRead(BaseModel):
    id: str = Field(...)
    driverId: str = Field(...)
    startLocation: str = Field(...)
    startLocationCoordinates: str = Field(...)
    destination: str = Field(...)
    destinationCoordinates: str = Field(...)
    stopPoints: Optional[List[str]] = Field(None)
    date: datetime = Field(...)
    time: str = Field(...)
    availableSeats: int = Field(...)
    tentativePrice: float = Field(...)
    carMake: str = Field(...)
    carModel: str = Field(...)
    carYear: int = Field(...)
    carColor: str = Field(...)
    carPlateNumber: str = Field(...)
    createdAt: datetime = Field(...)
    updatedAt: datetime = Field(...)
    bookings: Optional[List] = Field(None)
    status: RideStatus = Field(...)

    # Example validator for date:
    # @validator("date")
    # def validate_date(cls, v):
    #     try:
    #         datetime.fromisoformat(v)
    #         return v
    #     except ValueError:
    #         raise ValueError(
    #             "Invalid date format. Please use ISO 8601 format.")


class RideCreate(RideBase):
    model_config = ConfigDict(extra="forbid")

    password: Annotated[str, Field(
        pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Str1ngst!"])]


class RideUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(min_length=2, max_length=30, examples=[
                                      "Ride Rideberg"], default=None)]
    username: Annotated[
        str | None, Field(min_length=2, max_length=20,
                          pattern=r"^[a-z0-9]+$", examples=["userberg"], default=None)
    ]
    email: Annotated[EmailStr | None, Field(
        examples=["user.userberg@example.com"], default=None)]
    profile_image_url: Annotated[
        str | None,
        Field(
            pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", examples=["https://www.profileimageurl.com"], default=None
        ),
    ]


class RideDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
