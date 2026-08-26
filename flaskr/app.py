import os
from flask import (
    Flask,
    render_template,
)
from dotenv import load_dotenv, find_dotenv
import auth
import create

app = Flask(__name__)
app.register_blueprint(auth.auth)
app.register_blueprint(create.create)

load_dotenv(find_dotenv())


@app.route("/")
@app.route("/index")
def health():
    """Flask Health Check"""
    return render_template("index.html", health="OK")


if __name__ == "__main__":
    app.run(debug=True)
