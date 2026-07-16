from datetime import datetime, timezone

import os

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(
    host=os.getenv("MONGO_HOST", "localhost"), port=int(os.getenv("MONGO_PORT", 27017))
)

db = client["sfmshop_logs"]
logs_collection = db["logs"]


def save_log(log_data):
    if "timestamp" not in log_data:
        log_data["timestamp"] = datetime.now(timezone.utc)

    result = logs_collection.insert_one(log_data)

    return result.inserted_id


def get_logs_by_type(event_type):
    logs = logs_collection.find({"event_type": event_type})
    return list(logs)


def get_logs_by_status_range(min_status, max_status):
    logs = logs_collection.find(
        {"status_code": {"$gte": min_status, "$lt": max_status}}
    )
    return list(logs)


def get_logs_by_date_range(start_date, end_date):
    logs = logs_collection.find({"timestamp": {"$gte": start_date, "$lt": end_date}})
    return list(logs)


def create_log_indexes():
    logs_collection.create_index("event_type")
    logs_collection.create_index("status_code")
    logs_collection.create_index("timestamp")


def get_log_by_id(log_id):
    log = logs_collection.find_one({"_id": ObjectId(log_id)})

    return log


def update_log_message(log_id, new_message):
    result = logs_collection.update_one(
        {"_id": ObjectId(log_id)}, {"$set": {"message": new_message}}
    )

    return result.modified_count


def delete_log(log_id):
    result = logs_collection.delete_one({"_id": ObjectId(log_id)})
    return result.deleted_count
