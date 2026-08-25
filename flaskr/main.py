from flask import Flask, render_template, request

#mongodb 연결
from dotenv import load_dotenv
import os
from pymongo import MongoClient
load_dotenv()
mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)
db = client["mini_project"]
projects = db["projects"]
####


#mongodb 연결 테스트
try: 
    client.admin.command("ping")
    print("MongoDB 연결 성공!")
except Exception as e:
    print("MongoDB 연결 실패:", e) 
####

app = Flask(__name__)
@app.route("/create", methods=["GET", "POST"])

def create_project():
   if request.method == "POST":
        new_project = {
        "title": request.form.get("title"),
        "team": request.form.get("team"),
        "description": request.form.get("description"),
        "start_date": request.form.get("start_date"),
        "end_date": request.form.get("end_date"),
        }
        projects.insert_one(new_project)
        return """
    <script>
        alert("프로젝트 생성 성공!");
        window.location.href = 
        "/";
    </script>
    """
   return render_template("create.html")


#프로젝트 생성 완료되면 메인 페이지로 새로고침되어야 함 (메인 페이지 코드 merge되면 교체 필요)
@app.route("/")
def home():
    return "메인페이지 (임시 메세지)"

