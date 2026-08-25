from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def health():
    return render_template("index.html", health="OK")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return
