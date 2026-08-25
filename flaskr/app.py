import os
from flask import Flask, request, render_template, make_response, url_for
from dotenv import load_dotenv, find_dotenv

from datetime import datetime, timezone, timedelta
import jwt

load_dotenv(find_dotenv())

app = Flask(__name__)

# TODO: in-memory. Production or DB 연동 시 제거
users = {
    "admin": "admin",
}

tokens = {}


@app.route("/")
@app.route("/index")
def health():
    """Flask Health Check"""
    return render_template("index.html", health="OK")


@app.route("/login", methods=["GET", "POST"])
def login():
    """로그인에 대한 GET, POST 요청을 분리합니다."""
    if request.method == "GET":
        return get_login_form()
    else:
        return post_login_form()


def get_login_form():
    """로그인 페이지를 반환합니다."""
    access_token = request.cookies.get("access_token")
    if not access_token:
        return render_template("auth/login.html")
    else:
        secret_key = os.getenv("JWT_SECRET_KEY")
        decoded_token = jwt.decode(
            jwt=access_token,
            key=secret_key,
            algorithms=["HS256"],
        )
        username = decoded_token["username"]

        if username in users:
            return render_template("index.html")


def post_login_form():
    """사용자의 아이디, 비밀번호를 받고 로그인을 시도합니다.

    1. 클라이언트 측에 쿠키에 access_token이 있는지 검사합니다.
    2. access_token이 없거나 기한이 만료되었을 경우, 재로그인 합니다.
    3. access_token이 있고, 기한이 아직 지나지 않았고, 올바른 형태로 검증이 되었으면 로그인을 하지 않습니다.

    """
    access_token = request.cookies.get("access_token")
    if not access_token:
        username = request.form.get("username")
        password = request.form.get("password")

        username = username.rstrip()
        password = password.rstrip()

        if len(username) > int(os.getenv("LOGIN_MAX_LENGTH")) or len(password) > int(
            os.getenv("LOGIN_MAX_LENGTH")
        ):
            return render_template("auth/login.html")

        if username in users and users[username] == password:
            payload = {
                "user_id": 1,
                "username": username,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            }
            secret_key = os.getenv("JWT_SECRET_KEY")

            encoded_token = jwt.encode(
                payload=payload,
                key=secret_key,
                algorithm="HS256",
            )

            response = make_response(render_template("auth/login_success.html"))
            response.set_cookie("access_token", encoded_token)

            tokens[username] = encoded_token
            return response
        else:
            return render_template("auth/login.html")
    else:
        secret_key = os.getenv("JWT_SECRET_KEY")
        decoded_token = jwt.decode(
            jwt=access_token,
            key=secret_key,
            algorithms=["HS256"],
        )
        username = decoded_token["username"]

        if username in users:
            return render_template("auth/login_success.html")

if __name__ == "__main__":
    app.run(debug=True)
