from motor.motor_asyncio import AsyncIOMotorClient

from config import (
    MONGO_URL,
    MONGO_URL_2,
    DB_NAME,
    DB_NAME_2
)

client1 = AsyncIOMotorClient(MONGO_URL)
db1 = client1[DB_NAME]

client2 = AsyncIOMotorClient(MONGO_URL_2)
db2 = client2[DB_NAME_2]

files_col_1 = db1["files"]
files_col_2 = db2["files"]

users_col = db1["users"]
requests_col = db1["requests"]


async def create_indexes():

    await files_col_1.create_index("file_name")
    await files_col_1.create_index("search_text")
    await files_col_1.create_index("caption")

    await files_col_2.create_index("file_name")
    await files_col_2.create_index("search_text")
    await files_col_2.create_index("caption")

    await users_col.create_index("user_id")
    await requests_col.create_index("user_id")

    print("MongoDB 1 Connected ✅")
    print("MongoDB 2 Connected ✅")
    print("Indexes Created ✅")
