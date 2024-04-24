import uuid
from datetime import datetime
from enum import Enum
from typing import Annotated, Optional, List, Any, Type, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, validator, constr
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: dict[str, Any], b):
        # This method is used by Pydantic to populate the schema for OpenAPI
        if field_schema is not None:
            field_schema.update(type="string", format="ObjectId",
                                example=str(ObjectId()))

    @classmethod
    def validate(cls, v, b):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

    def __class_getitem__(cls, item: Type) -> Type:
        # This method might be required for Pydantic to correctly identify the class in certain situations
        return cls


class RideStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Point(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float]

class Location(BaseModel):
    name: str
    location: Point

class CarDetails(BaseModel):
    make: Optional[str]
    model: Optional[str]
    year: Optional[int]
    color: Optional[str]
    plateNumber: str


class Capacity(BaseModel):
    total: int
    occupied: int


class Bookings(BaseModel):
    userId: str
    startPoint: Location
    endPoint: Location

# TODO: check how to use this custom verifier without breaking /docs for swagger


class RideBase(BaseModel):
    # id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    driverUserId: str = Field(...)
    startPoint: Location = Field(...)
    endPoint: Location = Field(...)
    stopPoints: Optional[List[Location]] = Field(None)
    capacity: Capacity = Field(...)
    car: CarDetails = Field(...)
    bookings: Optional[List[Bookings]] = Field(None)
    status: RideStatus = Field(...)
    date: datetime = Field(...)
    priceSeat: float = Field(...)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class RideWithId(RideBase):
        id: str = Field(..., alias="_id")

class RideRead(BaseModel):
    result: List[RideWithId]
    page: int
    total: int
    totalPages: int


class RideCreate(RideBase):
    pass


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
