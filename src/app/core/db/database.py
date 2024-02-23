from motor.motor_asyncio import AsyncIOMotorClient

PASSWORD = "1lfNsyKaid6DTlYx"
DB_NAME = "carcool"

# Your MongoDB connection details
MONGO_DETAILS = f"mongodb+srv://VibeWheels1:{PASSWORD}@cluster0.zcdbnsk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = AsyncIOMotorClient(MONGO_DETAILS)


def get_db_client():
    return client[DB_NAME]


def get_collection(collection_name):
    return get_db_client()[collection_name]


async def close_mongo():
    await client.close()
    print('DB closed')


class Base():
    pass
