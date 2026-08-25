# kraftonjungle-w0-project

# 실행

환경 설정
```bash
uv init
un venv
uv add flask gunicorn
.venv/Scripts/activate
```

로컬 서버 실행
```
gunicorn --bind localhost:8000 app:app
localhost:8000 접속
```
