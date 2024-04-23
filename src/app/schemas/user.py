from pydantic import BaseModel, Field
from typing import List, Optional

class CarInfo(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    plate_number: Optional[str] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    car_info: Optional[CarInfo] = None
    profile_picture: Optional[str] = None
    preferences: Optional[List[str]] = []

class UserCreate(BaseModel):
    firebase_uid: str = Field(..., alias="firebaseUID")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    car_info: Optional[CarInfo] = None
    profile_picture: Optional[str] = None
    preferences: Optional[List[str]] = []

    class Config:
        allow_population_by_field_name = True

class UserRead(BaseModel):
    id: str = Field(..., alias='_id')
    firebase_uid: str = Field(..., alias="firebaseUID")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    car_info: Optional[CarInfo] = None
    profile_picture: Optional[str] = None
    preferences: List[str] = []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
