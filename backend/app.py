from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from routes import register_routes
from render import register_renders

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Inicializar SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Registrar rutas y vistas
register_routes(app)
register_renders(app)

# Pasar instancia de socketio a los blueprints
from routes.acciones import set_socketio
set_socketio(socketio)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
