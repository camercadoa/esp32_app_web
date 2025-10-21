from flask import Flask
from render.renders import auth_web, app_web

def register_renders (app: Flask):
    app.register_blueprint(auth_web)
    app.register_blueprint(app_web)