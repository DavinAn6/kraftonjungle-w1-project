import json
from bson.objectid import ObjectId
from flask import Blueprint, render_template, request, jsonify, redirect
from db import get_db

db = get_db()
projects = db["projects"]
users = db["users"]

create = Blueprint("create", __name__)


@create.route("/create", methods=["GET", "POST"])
def create_project():
    """프로젝트 페이지 라우터입니다."""
    if request.method == "POST":
        return post_create_form()
    else:
        return get_create_form()


def get_create_form():
    """프로젝트 생성 페이지를 반환합니다."""
    return render_template("create.html")


def post_create_form():
    """프로젝트를 생성하는 페이지입니다."""
    members_json = request.form.get("members")
    members = json.loads(members_json) if members_json else []

    new_project = {
        "title": request.form.get("title"),
        "team": request.form.get("team"),
        "description": request.form.get("description"),
        "start_date": request.form.get("start_date"),
        "end_date": request.form.get("end_date"),
        "members": members,
    }
    projects.insert_one(new_project)
    return redirect("/dashboard")


@create.route("/api/users/search")
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
