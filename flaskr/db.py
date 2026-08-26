from dotenv import load_dotenv
import os
from pymongo import MongoClient
load_dotenv()
mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)
db = client["mini_project"]

def get_db():
    return db