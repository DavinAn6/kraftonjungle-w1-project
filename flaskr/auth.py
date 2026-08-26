import os
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, InvalidSignatureError
from functools import wraps

from flask import (
    request,
    render_template,
    redirect,
    make_response,
    Blueprint,
    jsonify,
)

from datetime import datetime, timezone, timedelta
import hashlib
from hmac import compare_digest
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# TODO: 추후 db.py로 책임 분리
client = MongoClient(os.getenv("MONGODB_URI"))
users_db = client.get_database("mini_project").get_collection("users")

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
    except InvalidSignatureError:
        return None


def generate_token(user_id, expiration=30):
    """JWT 토큰을 발급합니다.

    1. payload에는 sub(mongoDB _id), iat(현재 시간), exp(만료 시간=30분후)가 설정됩니다.
    2. secret_key를 env 파일에서 가져옵니다.
    3. JWT 토큰을 인코딩하여 반환합니다. HS256 기준입니다.
    """
    headers = {
        "alg": "HS256",
        "typ": "JWT",
    }
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),  # TODO: ID 대신 이메일 고려
        "iat": now,
        "exp": now + timedelta(minutes=expiration),
    }
    secret_key = os.getenv("JWT_SECRET_KEY")

    encoded_token = jwt.encode(
        headers=headers,
        payload=payload,
        key=secret_key,
        algorithm="HS256",
    )
    return encoded_token


def login_required(func):
    @wraps(func)
    def validation(*args, **kwargs):
        """JWT 검증 데코레이터 입니다.
        토큰이 유효하지 않을 시 브라우저 쿠키에 있는 토큰을 파기합니다.
        사용법은 인증이 필요한 API 아래에 적으시면 됩니다.

        ex)
        @app.route("URL")
        @login_required <- 여기
        """
        access_token = request.cookies.get("access_token")
        payload = verify_access_token(access_token)
        if not payload:
            response = make_response(redirect("/login"))
            response.delete_cookie("access_token")
            return response
        return func(*args, **kwargs)

    return validation


def is_logged_in():
    access_token = request.cookies.get("access_token")
    return verify_access_token(token=access_token) is not None


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
    if is_logged_in():
        return redirect("/index")
    return render_template("auth/login_page.html")


def post_login_form():
    """사용자의 아이디, 비밀번호를 받고 로그인을 시도합니다.

    1. JWT 토큰을 검증하고, 유효할 시 /index로 리디렉션 됩니다.
    2. JWT 토큰이 유효하지 않을 시 로그인 합니다.
    3. 아이디와 패스워드 길이를 검사합니다. 최대 길이는 50입니다.
    4. 아이디와 패스워드가 DB에 존재할 경우, JWT 토큰을 새로 발급합니다. 만료 시간은 30분 입니다.
    """
    if is_logged_in():
        return redirect("/index")

    username = request.form.get("username").rstrip()
    password = request.form.get("password").rstrip()

    if len(username) > int(os.getenv("LOGIN_MAX_LENGTH")) or len(password) > int(
        os.getenv("LOGIN_MAX_LENGTH")
    ):
        return redirect("/login")
    try:
        user = users_db.find_one({"ID": username})
        if not user:
            return redirect("/login")
    except PyMongoError:
        return redirect("/login")

    # TODO: Production 환경에서는 secure=True
    if verify_password(user=user, password=password):
        access_token = generate_token(user_id=user["_id"], expiration=30)

        response = make_response(
            render_template("auth/login_success.html", username=username)
        )
        response.set_cookie(
            "access_token",
            access_token,
            samesite="Lax",
            httponly=True,
        )

        return response
    return redirect("/login")


@auth.post("/logout")
def logout():
    """사이트로부터 로그아웃을 시도합니다.

    1. access_token을 삭제합니다.
    2. 로그인 페이지로 리디렉션 됩니다.
    """
    response = make_response(redirect("/login"))
    response.delete_cookie("access_token")

    return response


@auth.route("/signin", methods=["GET", "POST"])
def signin():
    """회원가입 페이지에 대한 GET, POST 요청을 분리합니다."""
    if request.method == "GET":
        return get_signin_form()
    else:
        return post_signin_form()


def get_signin_form():
    """회원가입 페이지를 반환합니다.

    1. 현재 로그인 되어있을 시 /index 페이지로 리디렉션 됩니다.
    2. 로그인 되어있지 않으면 회원가입페이지를 반환합니다.
    """
    if is_logged_in():
        return redirect("/index")
    return render_template("auth/signin_page.html")


def post_signin_form():
    """사용자의 정보를 받고, 회원가입을 시도합니다.

    1. JWT 토큰을 검증하고, 유효할 시 /index로 리디렉션 됩니다.
    2. JWT 토큰이 유효하지 않을 시 회원가입 합니다.
    3. 각 항목이 DB에 들어가도 문제없을지 검증합니다.
    """
    if is_logged_in():
        return redirect("/index")

    name = request.form.get("name", "").rstrip()
    username = request.form.get("username", "").rstrip()
    email = request.form.get("email", "").rstrip()
    password = request.form.get("password", "").rstrip()
    jungle = int(request.form.get("jungle", 0))
    classroom = int(request.form.get("classroom", 0))

    # TODO: 백엔드 검증 루틴 추가
    salt = os.urandom(16)
    hashed = encode_password(password=password, salt=salt)

    data = {
        "name": name,
        "ID": username,
        "email": email,
        "password": {
            "salt": salt,
            "hashed": hashed,
        },
        "jungle": jungle,
        "classroom": classroom,
    }

    try:
        users_db.insert_one(data)
        return redirect("/login")
    except PyMongoError:
        return redirect("/signin")


@auth.post("/signin/check/username")
def check_username():
    """사용자 아이디가 DB에서 중복되는 지 검사합니다.

    1. 프론트엔드에서 아이디 중복 확인을 누르면
    2. 이 API에서 DB에 접근하여 중복된 아이디인지 검사합니다.
    3. 중복되어있지 않으면 True, 중복되어있으면 False를 반환합니다.
    """
    username = request.form.get("username", "").rstrip()
    try:
        duplicated = users_db.find_one({"ID": username})
        return jsonify(duplicated is None)
    except PyMongoError:
        return jsonify(False)


@auth.post("/signin/check/email")
def check_email():
    """사용자 이메일이 DB에서 중복되는 지 검사합니다.

    1. 프론트엔드에서 이메일 중복 확인을 누르면
    2. 이 API에서 DB에 접근하여 중복된 이메일인지 검사합니다.
    3. 중복되어있지 않으면 True, 중복되어있으면 False를 반환합니다.
    """
    email = request.form.get("email", "").rstrip()
    try:
        duplicated = users_db.find_one({"email": email})
        return jsonify(duplicated is None)
    except PyMongoError:
        return jsonify(False)


def encode_password(password, salt):
    """비밀번호 해시함수입니다.

    비밀번호는 DB에 평문으로 저장하지 않고, 해시값으로 저장합니다.
    비밀번호 검증시, 입력값을 저장되어있는 해시값과 비교하기 위함입니다.
    같은 비밀번호라도, salt값에 따라 달라지므로 사용자를 구분할 수 있습니다.

    1. 비밀번호를 UTF-8로 인코딩합니다.
    2. 16바이트 Salt값을 생성합니다.
    3. sha256 알고리즘으로 100000회 반복하여 생성합니다.
    """
    password = password.encode("utf-8")

    hashed_password = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=password,
        salt=salt,
        iterations=100000,
    ).hex()

    return hashed_password


def verify_password(user, password):
    """비밀번호 검증 함수입니다.

    비밀번호를 생성할 때 같이 저장했던 솔트값을 이용하여 비교합니다.
    DB에 저장되어있는 해시값과, 현재 받은 비밀번호를 다시 해시한 값을 비교하여
    동일한지 검증합니다.
    """
    db_salt = user["password"]["salt"]
    db_password = user["password"]["hashed"]

    hashed_password = encode_password(password=password, salt=db_salt)
    return compare_digest(hashed_password, db_password)
