from flask import (
    Flask,
    render_template,
)
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import auth
from auth import login_required
import create
import detail
import task

app = Flask(__name__)
app.register_blueprint(auth.auth)
app.register_blueprint(create.create)
app.register_blueprint(detail.detail)
app.register_blueprint(task.task)


@app.route("/")
@app.route("/index")
@login_required
def health():
    """Flask Health Check"""
    return render_template("index.html", health="OK")


if __name__ == "__main__":
    app.run(debug=True)
