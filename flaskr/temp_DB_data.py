from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["mini_project"]

project_info = db["project_info"]
tasks = db["tasks"]

project_info.delete_many({})
tasks.delete_many({})

# generate real ObjectIds up front, so we can reference them in tasks below
id_pipeline = ObjectId()
id_login = ObjectId()
id_notification = ObjectId()
id_test1 = ObjectId()
id_test2 = ObjectId()

# --- Project info ---
project_info.insert_many([
    {
        "_id": id_pipeline,
        "title": "프로젝트 1 : 인원 안다빈",
        "members": ["안다빈"],
        "start_date": "2026-01-01",
        "end_date": "2026-01-01"
    },
    {
        "_id": id_login,
        "title": "프로젝트 2 : 인원 양웅진",
        "members": ["양웅진"],
        "start_date": "2026-01-01",
        "end_date": "2026-01-01"
    },
    {
        "_id": id_notification,
        "title": "프로젝트 3 : 인원 안도하",
        "members": ["안도하"],
        "start_date": "2026-01-01",
        "end_date": "2026-01-01"
    },
    {
        "_id": id_test1,
        "title": "프로젝트 4 : 인원 안다빈 양웅진",
        "members": ["안다빈", "양웅진"],
        "start_date": "2026-01-01",
        "end_date": "2026-01-01"
    },
    {
        "_id": id_test2,
        "title": "프로젝트 5 : 인원 안도하 양웅진",
        "members": ["안도하", "양웅진"],
        "start_date": "2026-01-01",
        "end_date": "2026-01-01"
    }
])

# --- Tasks ---
tasks.insert_many([
    {
        "project_id": id_pipeline,
        "agenda": "CI/CD 파이프라인 개선 Test Agenda",
        "due_date": "2026-01-01",
        "owner": "안다빈",
        "status": "done"
    },
    {
        "project_id": id_pipeline,
        "agenda": "CI/CD 파이프라인 개선 Test Agenda1",
        "due_date": "2026-01-01",
        "owner": "안다빈",
        "status": "done"
    },
    {
        "project_id": id_pipeline,
        "agenda": "CI/CD 파이프라인 개선 Test Agenda2",
        "due_date": "2026-01-01",
        "owner": "안다빈",
        "status": "done"
    },
    {
        "project_id": id_pipeline,
        "agenda": "Test Agenda3",
        "due_date": "2026-01-01",
        "owner": "안다빈",
        "status": "done"
    },
    {
        "project_id": id_login,
        "agenda": "로그인/회원가입 시스템 개편 Test Agenda",
        "due_date": "2026-01-01",
        "owner": "안다빈",
        "status": "done"
    },
    {
        "project_id": id_notification,
        "agenda": "알림센터 구축 Test Agenda",
        "due_date": "2026-01-01",
        "owner": "안다빈",
        "status": "done"
    }
])

print("Seeded project_info:", project_info.count_documents({}))
print("Seeded tasks:", tasks.count_documents({}))