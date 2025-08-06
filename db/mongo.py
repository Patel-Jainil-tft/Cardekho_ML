from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "cardekho_mcp")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "cardekho_mcp")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def save_agent_response(payload: dict):
    return collection.insert_one(payload)
