from flask import Blueprint, render_template

auth_web = Blueprint("auth", __name__)

@auth_web.route("/login")
def login():
    return render_template("auth/login.html")

@auth_web.route("/registro")
def registro():
    return render_template("auth/registro.html")


dashboard_web = Blueprint("dashboard", __name__)

@dashboard_web.route("/")
def dashboard():
    return render_template("dashboard/dashboard.html")