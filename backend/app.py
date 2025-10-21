from flask import Flask
from flask_cors import CORS
from routes import register_routes
from render import register_renders

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

register_routes(app)
register_renders(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
