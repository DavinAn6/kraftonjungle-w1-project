import os
from flask import (
    Flask,
    render_template,
)
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import auth
from auth import login_required


app = Flask(__name__)
app.register_blueprint(auth.auth)


@app.route("/")
@app.route("/index")
@login_required
def health():
    """Flask Health Check"""
    return render_template("index.html", health="OK")


if __name__ == "__main__":
    app.run(debug=True)
