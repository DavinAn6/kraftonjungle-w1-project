import json
import re
from flask import Blueprint, g, render_template, request, jsonify, redirect
from auth import login_required
from db import get_db

db = get_db()
projects = db["projects"]
users = db["users"]

create = Blueprint("create", __name__)


@create.route("/create", methods=["GET", "POST"])
@login_required
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
    try:
        members = json.loads(members_json) if members_json else []
    except json.JSONDecodeError:
        return "Invalid members", 400

    if not isinstance(members, list) or any(
        not isinstance(member, dict)
        or not isinstance(member.get("name"), str)
        or not isinstance(member.get("email"), str)
        for member in members
    ):
        return "Invalid members", 400

    current_member = {"name": g.user["name"], "email": g.user["email"]}
    if not any(member["email"] == current_member["email"] for member in members):
        members.append(current_member)

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
@login_required
def search_member():
    """초대할 수 있는 팀원 목록을 조회할 수 있는 API입니다."""
    search_member = request.args.get("search_member", "").strip()
    if not search_member:
        return jsonify([])

    results = users.find(
        {
            "$or": [
                {"name": {"$regex": re.escape(search_member), "$options": "i"}},
                {"email": {"$regex": re.escape(search_member), "$options": "i"}},
            ]
        }
    ).limit(20)

    user_list = []
    for user in results:
        user_list.append({"name": user.get("name"), "email": user.get("email")})
    return jsonify(user_list)
