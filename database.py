from pymongo import MongoClient
from config import MONGO_URL, DB_NAME

client = MongoClient(MONGO_URL)

db = client[DB_NAME]

files_col = db["files"] 

users_col = db["users"]

requests_col = db["requests"]

print("MongoDB Connected ✅")