from typing import Any, List
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from ...schemas.user import UserCreate, UserRead, UserUpdate
from ...core.db.database import get_db_client
from bson import ObjectId, errors
from ...firebase_auth import get_current_user
from ...services.vibescore import average_vector

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


async def get_user_by_firebase_uid(firebase_uid: str):
    if not firebase_uid:
        raise ValueError("Firebase UID not provided")

    user = await mongo.find_one({"firebaseUID": firebase_uid})
    if user is None:
        raise ValueError("User not found")

    user['_id'] = str(user['_id'])
    return user

async def get_user_preference_vectors(user_ids):
    object_ids = [ObjectId(id) for id in user_ids]
    query = {"_id": {"$in": object_ids}}
    users = await mongo.find(query).to_list(None)  # Fetch all users in one go
    #print(users)
    user_vectors = {}
    user_details = {}
    for user in users:
        user_id_str = str(user['_id']) 
        user_vectors[user_id_str] = user.get('preferences_vector', [])
        user_details[user_id_str] = {"name": user.get('first_name')+ " " + user.get('last_name')}
    
    return (user_vectors, user_details)



@router.get("/firebase/", response_model=UserRead)
async def get_user_by_firebase(request: Request, firebase_user: dict = Depends(get_current_user)):
    try:
        user = await get_user_by_firebase_uid(firebase_user.get("uid"))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return user


@router.put("/update", response_model=UserRead)
async def update_user(request: Request, update_data: UserUpdate, firebase_user: dict = Depends(get_current_user)):
    firebase_uid = firebase_user.get("uid")
    if not firebase_uid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firebase UID not found")

    try:
        update_data = jsonable_encoder(update_data)
        update_data["preferences_vector"] = average_vector(update_data["preferences"]).tolist()
        print(update_data["preferences"])
        result = await mongo.update_one({"firebaseUID": firebase_uid}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        updated_user = await mongo.find_one({"firebaseUID": firebase_uid})
        if updated_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to fetch updated user")

        updated_user['_id'] = str(updated_user['_id'])
        return updated_user
    except errors.PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")