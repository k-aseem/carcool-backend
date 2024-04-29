from typing import Any, Annotated, List
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query, Body
from fastapi.encoders import jsonable_encoder
from ...core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from ...schemas.ride import RideRead, RideBase, RideCreate, RideWithId
from ...crud.crud_rides import crud_ride
from ...core.db.database import get_db_client
from bson import ObjectId
from datetime import datetime, timedelta
from ...firebase_auth import get_current_user
from .users import get_user_by_firebase_uid, get_user_preference_vectors
from ...services.vibescore import get_vibescore
import random
import re

router = APIRouter(prefix="/rides", tags=["rides"])

MONGO_COLLECTION_NAME = "rides"
MONGO_CLIENT = get_db_client()
mongo = MONGO_CLIENT[MONGO_COLLECTION_NAME]

PAGE_SIZE = 12


@router.post("/ride", status_code=status.HTTP_201_CREATED, response_model=RideRead)
async def post_ride(request: Request, user_ride: RideCreate, firebase_user: dict = Depends(get_current_user)):
    # db_user: RideRead | None = await crud_ride.get(
    #     db=db, schema_to_select=RideRead, username=username, is_deleted=False
    # )
    # if db_user is None:
    #     raise NotFoundException("User not found")
    firebase_uid = firebase_user.get("uid")
    if not firebase_uid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firebase UID not found")
    current_user = await get_user_by_firebase_uid(firebase_uid)
    ride_id = None
    try:
        print("HELLO HERE")
        user_ride = jsonable_encoder(user_ride)
        user_ride["driverUserId"] = current_user['_id'];
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

        retObject = {
            'result': created_ride,
            'page': 1,
            'total': 1,
            'totalPages': 1
        }
        print(retObject)
        return retObject

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
        'total': total,
        'totalPages': 1
    }




# get ride with id


@router.get("/ride/{ride_id}", response_model=RideRead)
async def get_ride(request: Request, ride_id: str, firebase_user: dict = Depends(get_current_user)):
    firebase_uid = firebase_user.get("uid")
    if ride_id is None or (not ObjectId.is_valid(ride_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid ride id")

    response = [await mongo.find_one({"_id": ObjectId(ride_id)})]

    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Ride not found")
    
    user_ids = []
    for doc in response:
        doc['_id'] = str(doc['_id'])
        user_ids.append(doc['driverUserId'])
    user_vectors, user_details = await get_user_preference_vectors(user_ids)
    print(user_details)
    current_user = await get_user_by_firebase_uid(firebase_uid)
    current_user_vector = current_user.get('preferences_vector', [])

    # Calculate vibe scores
    vibe_scores = get_vibescore(str(current_user['_id']), current_user_vector, user_vectors)
    for doc in response:
        doc['vibeScore'] = next((score for user_id, score in vibe_scores if user_id == doc['driverUserId']), 0)
        doc['vibeScore']=(int)(doc['vibeScore']*100)
        doc['userName'] = user_details[doc['driverUserId']]['name']

    return {
        'result': response,
        'page': 1,
        'total': 1,
        'totalPages': 1
    }


@router.get("/driver/{driver_user_id}", response_model=List[RideWithId])
async def get_rides_for_driver(firebase_user: dict = Depends(get_current_user)):
    firebase_uid = firebase_user.get("uid")
    if not firebase_uid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firebase UID not found")
    current_user = await get_user_by_firebase_uid(firebase_uid)
    now = datetime.now()
    rides = await mongo.find({
        "driverUserId": str(current_user['_id']),
        "date": {"$gte": now.isoformat()}
    }).sort("date", 1).to_list(length=5) 
    for ride in rides:
        ride['_id'] = str(ride['_id'])
    print(rides)
    return rides



@router.post("/search", response_model=RideRead)
async def search_rides(startLocation: List[float] = Body(...), endLocation: List[float] = Body(...), date: str = Body(...), sort: str = Body(...), page: int = Body(...), firebase_user: dict = Depends(get_current_user)):
    firebase_uid = firebase_user.get("uid")
    if not firebase_uid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firebase UID not found")
    try:
        print(sort)
        print(firebase_uid)
        search_date = datetime.strptime(date, "%Y-%m-%d")
        
        next_day = search_date + timedelta(days=1)

        max_distance = 20000
        # Constructing the query
        fromQuery = {
            "date": {"$gte": search_date.isoformat(), "$lt": next_day.isoformat()},
            "startPoint.location": {
                "$nearSphere": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": startLocation
                    },
                    "$maxDistance": max_distance
                }
            },
        }

        toQuery = {
            "date": {"$gte": search_date.isoformat(), "$lt": next_day.isoformat()},
            "endPoint.location": {
                "$nearSphere": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": endLocation
                    },
                    "$maxDistance": max_distance
                }
            }
        }
        sortOnDB = "date";
        if(sort=="lowestPrice"):
            sortOnDB = "priceSeat"
        fromRides = await mongo.find(fromQuery).sort(sortOnDB, 1).to_list(length=10000)
        toRides = await mongo.find(toQuery).sort(sortOnDB, 1).to_list(length=10000)
        toRideMap = {}
        for ride in toRides:
            ride['_id'] = str(ride['_id'])
            toRideMap[ride['_id']] = ride;
        aggRides = []
        for ride in fromRides:
            if str(ride['_id']) in toRideMap:
                ride_data = toRideMap[str(ride['_id'])]
                if 'driverUserId' in ride_data and bool(re.match(r'^[0-9a-fA-F]{24}$', ride_data['driverUserId'])):
                    aggRides.append(ride_data)

                
        
        # After aggregating rides and extracting user IDs
        user_ids = list({ride['driverUserId'] for ride in aggRides})
        user_vectors, user_details = await get_user_preference_vectors(user_ids)
        print(user_details)
        current_user = await get_user_by_firebase_uid(firebase_uid)
        current_user_vector = current_user.get('preferences_vector', [])

        # Calculate vibe scores
        vibe_scores = get_vibescore(str(current_user['_id']), current_user_vector, user_vectors)
        
        # Append vibe scores to each ride
        for ride in aggRides:
            ride_id = str(ride['_id'])
            ride['vibeScore'] = next((score for user_id, score in vibe_scores if user_id == ride['driverUserId']), 0)
            ride['vibeScore']=(int)(ride['vibeScore']*100)
            ride['userName'] = user_details[ride['driverUserId']]['name']
        
        if(sort=="vibe"):
            aggRides.sort(key=lambda x: x['vibeScore'], reverse=True)

        # Handling pagination
        if page < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page number must be greater than 0")

        skip = (page - 1) * PAGE_SIZE
        total = len(aggRides)
        if total > 0 and skip >= total:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page number out of range")

        # Return paginated results
        return {
            'result': aggRides[skip:skip+PAGE_SIZE],
            'page': page,
            'total': total,
            'totalPages': (int)(total/PAGE_SIZE + 1)
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))






valid_locations = [
    {"name": "3500 Richmond Ln, Blacksburg, VA 24060, USA", "coordinates": [-80.4507745, 37.2140813]},
    {"name": "1214 University City Blvd, Blacksburg, VA 24060, USA", "coordinates": [-80.4341081, 37.2408491]},
    {"name": "New York, NY, USA", "coordinates": [-74.0059728, 40.7127753]},
    {"name": "Squires Student Center, 290 College Ave, Blacksburg, VA 24061, USA", "coordinates": [-80.4179766, 37.2296088]},
    {"name": "Herndon, VA 20170, USA", "coordinates": [-77.3860976, 38.9695545]},
    {"name": "Ottawa, ON, Canada", "coordinates": [-75.69719309999999, 45.4215296]},
    {"name": "White House, TN, USA", "coordinates": [-86.6654844, 36.46874320000001]},
    {"name": "Toronto, ON, Canada", "coordinates": [-79.3831843, 43.653226]},
    {"name": "Maryland, USA", "coordinates": [-76.64127119999999, 39.0457549]},
    {"name": "Blacksburg, VA, USA", "coordinates": [-80.4139393, 37.2295733]}
]

car_makes_models = [
    {"make": "BMW", "model": "3 Series", "color": "Green"},
    {"make": "Tesla", "model": "Model S", "color": "Red"},
    {"make": "Ford", "model": "Mustang", "color": "Blue"},
    {"make": "Toyota", "model": "Corolla", "color": "White"},
    {"make": "Honda", "model": "Civic", "color": "Black"},
    {"make": "Jeep", "model": "Wrangler", "color": "Charcoal"}
]

user_ids = ["6612bf9a29d162cfa6cfa45a", "66294c1a5565abfbbd5ff2da", "662991898348bb698a47b8f2", "662993ca8035b4fb4120e3d1", "6629942c8035b4fb4120e3d2", "662994e48035b4fb4120e3d3", "662996308035b4fb4120e3d4"]


@router.post("/populate/{record_count}")
async def populate_demo_data(record_count: int):
    try:
        demo_data = []
        for _ in range(record_count):
            user_id = random.choice(user_ids)  # Randomly pick a user
            start_index, end_index = random.sample(range(len(valid_locations)), 2)
            startPoint = valid_locations[start_index]
            endPoint = valid_locations[end_index]
            car_choice = random.choice(car_makes_models)
            ride_document = {
                "driverUserId": user_id,  # Use the randomly picked user ID
                "startPoint": {
                    "name": startPoint["name"],
                    "location": {"type": "Point", "coordinates": startPoint["coordinates"]}
                },
                "endPoint": {
                    "name": endPoint["name"],
                    "location": {"type": "Point", "coordinates": endPoint["coordinates"]}
                },
                "stopPoints": [],
                "capacity": {"total": random.randint(1, 6), "occupied": 0},
                "car": {
                    "make": car_choice["make"],
                    "model": car_choice["model"],
                    "year": random.randint(2010, 2022),
                    "color": car_choice["color"],
                    "plateNumber": f"DEMO{random.randint(100, 999)}"
                },
                "bookings": [],
                "status": "IN_PROGRESS",
                "date": (datetime.now() + timedelta(days=random.randint(0, 5))).isoformat(),  # Random date from today to +30 days
                "priceSeat": random.uniform(20, 100),
            }
            demo_data.append(ride_document)

        # Inserting demo data into the database
        result = mongo.insert_many(demo_data)
        return {"message": f"Successfully inserted {len(demo_data)} demo ride records."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))