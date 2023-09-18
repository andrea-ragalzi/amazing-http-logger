"""
Module for MongoDB connection and collection initialization.

This module provides the necessary code for connecting to a MongoDB server,
initializing the database and collections, and creating an index on the
"email" field of the "users" collection.

Dependencies:
    - mongo_client from pymongo: MongoClient class for connecting to a MongoDB
      server.
    - pymongo: pymongo module for MongoDB operations.
    - settings from app.config: settings module for accessing configuration
      variables.

Variables:
    - client (MongoClient): MongoClient instance for connecting to the MongoDB
      server.
    - db: The MongoDB database.
    - User: The "users" collection in the MongoDB database.
    - Log: The "logs" collection in the MongoDB database.

"""

from pymongo import mongo_client
import pymongo
from app.config import settings

client = mongo_client.MongoClient(
    settings.DATABASE_URL, serverSelectionTimeoutMS=5000)

try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception:  # pylint: disable=broad-except
    print("Unable to connect to the MongoDB server.")

db = client[settings.MONGO_INITDB_DATABASE]
User = db.users
Log = db.logs
User.create_index([("email", pymongo.ASCENDING)], unique=True)
