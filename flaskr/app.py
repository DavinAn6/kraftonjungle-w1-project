import os
from flask import (
    Flask,
    render_template,
)
from dotenv import load_dotenv, find_dotenv
import auth

app = Flask(__name__)
app.register_blueprint(auth.auth)

load_dotenv(find_dotenv())


@app.route("/")
@app.route("/index")
def health():
    """Flask Health Check"""
    return render_template("index.html", health="OK")


if __name__ == "__main__":
    app.run(debug=True)
