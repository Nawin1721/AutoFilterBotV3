from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URL, DB_NAME


# =========================
# MONGO CLIENT
# =========================

client = AsyncIOMotorClient(MONGO_URL)

db = client[DB_NAME]


# =========================
# COLLECTIONS
# =========================

files_col = db["files"]

users_col = db["users"]

requests_col = db["requests"]


# =========================
# CREATE INDEXES
# =========================

async def create_indexes():

    await files_col.create_index("file_name")

    await files_col.create_index("search_text")

    await files_col.create_index("caption")

    await users_col.create_index("user_id")

    await requests_col.create_index("user_id")

    print("MongoDB Connected ✅")

    print("Indexes Created ✅")
