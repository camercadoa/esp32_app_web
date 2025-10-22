from flask import Blueprint, render_template

auth_web = Blueprint("auth", __name__)


@auth_web.route("/login")
def login():
    return render_template("auth/login.html")


@auth_web.route("/registro")
def registro():
    return render_template("auth/registro.html")


app_web = Blueprint("app", __name__)


@app_web.route("/")
def home():
    return render_template("home.html")


@app_web.route("/control")
def control():
    return render_template("control.html")


@app_web.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app_web.route("/reportes")
def reportes():
    return render_template("reportes.html")


@app_web.route("/acerca_de")
def acerca_de():
    return render_template("acerca.html")
