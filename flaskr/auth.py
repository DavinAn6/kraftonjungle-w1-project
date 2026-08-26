import os
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from functools import wraps

from flask import (
    request,
    render_template,
    redirect,
    make_response,
    Blueprint,
)

from datetime import datetime, timezone, timedelta

# TODO: in-memory. Production or DB 연동 시 제거
users = {
    "admin": "admin",
}

auth = Blueprint("auth", __name__)


def verify_access_token(token):
    """JWT 토큰을 검증합니다. 정상적인 상황에서는 JWT 토큰을 decode하여 payload를 반환합니다.

    1. Expired 되었을 경우 None을 반환합니다.
    2. Token 형식이 올바르지 않을 경우 None을 반환합니다.
    """
    if not token:
        return None
    try:
        secret_key = os.getenv("JWT_SECRET_KEY")
        payload = jwt.decode(
            jwt=token,
            key=secret_key,
            algorithms=["HS256"],
        )
        return payload
    except ExpiredSignatureError:
        return None
    except InvalidTokenError:
        return None


def generate_token(username, expiration=30):
    """JWT 토큰을 발급합니다.

    1. payload에는 user_id, username, 만료 시간이 설정됩니다.
    2. secret_key를 env 파일에서 가져옵니다.
    3. JWT 토큰을 인코딩하여 반환합니다. HS256 기준입니다.
    """
    payload = {
        "user_id": 1,  # TODO: 추후 DB 연동 시, mongoDB의 _id 또는 user_id 항목으로 교체
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expiration),
    }
    secret_key = os.getenv("JWT_SECRET_KEY")

    encoded_token = jwt.encode(
        payload=payload,
        key=secret_key,
        algorithm="HS256",
    )
    return encoded_token


def login_required(func):
    @wraps(func)
    def validation(*args, **kwargs):
        access_token = request.cookies.get("access_token")
        payload = verify_access_token(access_token)
        if not payload:
            return redirect("/login")
        return func(*args, **kwargs)

    return validation


@auth.route("/login", methods=["GET", "POST"])
def login():
    """로그인에 대한 GET, POST 요청을 분리합니다."""
    if request.method == "GET":
        return get_login_form()
    else:
        return post_login_form()


def get_login_form():
    """로그인 페이지를 반환합니다.

    1. 쿠키에서 JWT 토큰을 가져옵니다.
    2. verify_access_token 으로 JWT 토큰을 검증합니다.
    3. 토큰이 유효하고, username이 DB에 존재하면 /index 페이지로 리디렉션 됩니다.
    4. 토큰 검증 실패 시 로그인 페이지를 반환합니다.
    """

    access_token = request.cookies.get("access_token")
    payload = verify_access_token(token=access_token)
    if payload:
        username = payload["username"]
        if username in users:
            return redirect("/index")
    return render_template("auth/login_page.html")


def post_login_form():
    """사용자의 아이디, 비밀번호를 받고 로그인을 시도합니다.

    1. JWT 토큰을 검증하고, 유효할 시 /index로 리디렉션 됩니다.
    2. JWT 토큰이 유효하지 않을 시 로그인 합니다.

    3. 아이디와 패스워드 길이를 검사합니다. 최대 길이는 50입니다.
    4. 아이디와 패스워드가 DB에 존재할 경우, JWT 토큰을 새로 발급합니다. 만료 시간은 30분 입니다.
    """
    access_token = request.cookies.get("access_token")
    payload = verify_access_token(token=access_token)
    if payload:
        username = payload["username"]
        if username in users:
            return redirect("/index")

    username = request.form.get("username").rstrip()
    password = request.form.get("password").rstrip()

    if len(username) > int(os.getenv("LOGIN_MAX_LENGTH")) or len(password) > int(
        os.getenv("LOGIN_MAX_LENGTH")
    ):
        return redirect("/login")

    if username in users and users[username] == password:  # TODO: 추후 DB 쿼리로 교체
        access_token = generate_token(username=username, expiration=30)

        response = make_response(
            render_template("auth/login_success.html", username=username)
        )
        response.set_cookie("access_token", access_token)
        response.set_cookie("username", username)

        return response
    else:
        return redirect("/login")


@auth.post("/logout")
def logout():
    """사이트로부터 로그아웃을 시도합니다.

    1. 쿠키에 JWT 토큰이 존재하는지 검사합니다.
    2. JWT 토큰이 존재하지 않는다면, /index 페이지로 리다이렉트됩니다.
    3. JWT 토큰이 존재한다면, 쿠키에서 값을 삭제합니다.
    4. login 페이지로 리다이렉트 됩니다.
    """
    response = make_response(redirect("/login"))
    response.delete_cookie("access_token")
    response.delete_cookie("username")

    return response
