from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
logging.info(f"Connecting to MongoDB at {MONGO_URI}")
DB_NAME = os.getenv("MONGO_DB_NAME", "cardekho_mcp")
logging.info(f"Using database: {DB_NAME}")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "cardekho_mcp")
logging.info(f"Using collection: {COLLECTION_NAME}")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def save_agent_response(payload: dict):
    try:
        return collection.insert_one(payload)
    except Exception:
        logging.exception("MongoDB insert failed.")
        return None