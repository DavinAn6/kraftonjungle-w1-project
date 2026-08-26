from auth import login_required
from flask import Blueprint, render_template, request, jsonify
from db import get_db

db = get_db()
projects = db["projects"]
users = db["users"]

create = Blueprint("create", __name__)


@create.route("/create", methods=["GET", "POST"])
@login_required
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
            window.location.href = "/";
        </script>
        """
    return render_template("create.html")


@create.route("/api/users/search")
@login_required
def search_member():
    search_member = request.args.get("search_member")
    results = users.find(
        {
            "$or": [
                {"name": {"$regex": search_member, "$options": "i"}},
                {"email": {"$regex": search_member, "$options": "i"}},
            ]
        }
    )

    user_list = []
    for user in results:
        user_list.append({"name": user.get("name"), "email": user.get("email")})
    return jsonify(user_list)
