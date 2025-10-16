from flask import Flask, render_template
from flask_cors import CORS

# Importar Blueprints
from routes.acciones import acciones_bp
from routes.estadisticas import estadisticas_bp
from routes.estado import estado_bp
from routes.health import health_bp

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Registrar Blueprints
app.register_blueprint(acciones_bp)
app.register_blueprint(estadisticas_bp)
app.register_blueprint(estado_bp)
app.register_blueprint(health_bp)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
