import os
from flask import Flask, request, render_template, make_response, url_for, redirect
from dotenv import load_dotenv, find_dotenv

from datetime import datetime, timezone, timedelta
import jwt
from jwt import ExpiredSignatureError

load_dotenv(find_dotenv())

app = Flask(__name__)

# TODO: in-memory. Production or DB 연동 시 제거
users = {
    "admin": "admin",
}


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
    """로그인 페이지를 반환합니다.

    1. 쿠키에서 JWT 토큰을 가져옵니다.
    2. JWT 토큰을 검사하여, username이 존재하면 health 페이지로 리다이렉트 됩니다.
    3. 존재하지 않으면 로그인 페이지를 반환합니다.
    """

    access_token = request.cookies.get("access_token")
    username = request.cookies.get("username")

    if not access_token:
        return render_template("auth/login_page.html")
    else:
        secret_key = os.getenv("JWT_SECRET_KEY")
        try:
            decoded_token = jwt.decode(
                jwt=access_token,
                key=secret_key,
                algorithms=["HS256"],
            )
        except ExpiredSignatureError:
            response = make_response(redirect(url_for("login")))
            response.delete_cookie("access_token")
            response.delete_cookie("username")
            return response

        username = decoded_token["username"]
        if username in users:
            return redirect(url_for("health"))


def post_login_form():
    """사용자의 아이디, 비밀번호를 받고 로그인을 시도합니다.

    1. 클라이언트 측에 쿠키에 access_token이 있는지 검사합니다.
    2. access_token이 없거나 기한이 만료되었을 경우, 로그인 합니다.
    3. access_token이 있을 시 만료 여부를 검사하고, login_success 페이지를 보여줍니다.
    TODO) 이미 로그인 되어있을 시 login_success가 아닌, 전에 있던 페이지로 리다이렉트하기

    """
    access_token = request.cookies.get("access_token")
    username = request.cookies.get("username")

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

            response = make_response(
                render_template("auth/login_success.html", username=username)
            )
            response.set_cookie("access_token", encoded_token)
            response.set_cookie("username", username)

            return response
        else:
            return redirect(url_for("login"))
    else:
        secret_key = os.getenv("JWT_SECRET_KEY")
        try:
            decoded_token = jwt.decode(
                jwt=access_token,
                key=secret_key,
                algorithms=["HS256"],
            )
        except ExpiredSignatureError:
            response = make_response(redirect(url_for("health")))
            response.delete_cookie("access_token")
            response.delete_cookie("username")
            return response
        username = decoded_token["username"]

        if username in users:
            return render_template("auth/login_success.html", username=username)


@app.post("/logout")
def logout():
    """사이트로부터 로그아웃을 시도합니다.

    1. 쿠키에 JWT 토큰이 존재하는지 검사합니다.
    2. JWT 토큰이 존재하지 않는다면, /index 페이지로 리다이렉트됩니다.
    3. JWT 토큰이 존재한다면, 쿠키에서 값을 삭제합니다.
    4. login 페이지로 리다이렉트 됩니다.
    """
    access_token = request.cookies.get("access_token")
    username = request.cookies.get("username")

    if not access_token or not username:
        return redirect(url_for("health"))
    else:
        response = make_response(redirect(url_for("login")))
        response.delete_cookie("access_token")
        response.delete_cookie("username")

        return response


if __name__ == "__main__":
    app.run(debug=True)
