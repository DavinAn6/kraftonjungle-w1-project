import os
from pymongo import MongoClient

mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)
db = client["mini_project"]


def get_db():
    return db
