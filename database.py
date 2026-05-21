from pymongo import MongoClient
from config import MONGO_URL, DB_NAME

client = MongoClient(MONGO_URL)

db = client[DB_NAME]

files_col = db["files"] 

users_col = db["users"]

requests_col = db["requests"]

# =========================
# DATABASE INDEXES
# =========================

files_col.create_index("file_name")

files_col.create_index("search_text")

files_col.create_index("caption")

users_col.create_index("user_id")

requests_col.create_index("user_id")


print("MongoDB Connected ✅")
print("Indexes Created ✅")
