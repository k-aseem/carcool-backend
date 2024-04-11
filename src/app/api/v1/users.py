from typing import Any, List
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from ...schemas.user import UserCreate, UserRead
from ...core.db.database import get_db_client
from bson import ObjectId
from ...firebase_auth import get_current_user 

router = APIRouter(prefix="/users", tags=["users"])

MONGO_COLLECTION_NAME = "users"
MONGO_CLIENT = get_db_client()
mongo = MONGO_CLIENT[MONGO_COLLECTION_NAME]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def create_user(request: Request, user_data: UserCreate, user: dict = Depends(get_current_user)):
    try:
        print(user_data)
        user_data = jsonable_encoder(user_data)
        response = await mongo.insert_one(user_data)

        if response is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

        user_id = response.inserted_id
        created_user = await mongo.find_one({"_id": ObjectId(user_id)})

        if created_user is None:
            await mongo.delete_one({"_id": ObjectId(user_id)})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

        created_user['_id'] = str(created_user['_id'])

        return created_user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{user_id}", response_model=UserRead)
async def get_user(request: Request, user_id: str):
    if user_id is None or (not ObjectId.is_valid(user_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")

    user = await mongo.find_one({"_id": ObjectId(user_id)})

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user['_id'] = str(user['_id'])

    return user


@router.get("/", response_model=List[UserRead])
async def get_all_users(request: Request):
    users = await mongo.find().to_list(length=100)  # Adjust the length as needed

    for user in users:
        user['_id'] = str(user['_id'])

    return users
