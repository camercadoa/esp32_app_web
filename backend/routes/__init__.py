from flask import Flask
from routes.acciones import acciones_bp
from routes.dispositivos import dispositivos_bp
from routes.usuarios import usuarios_bp
from routes.sesiones import sesiones_bp
from routes.estado import estado_bp
from routes.estadisticas import estadisticas_bp
from routes.reportes import reportes_bp
from routes.health import health_bp

def register_routes(app: Flask):
    app.register_blueprint(acciones_bp)
    app.register_blueprint(dispositivos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(sesiones_bp)
    app.register_blueprint(estado_bp)
    app.register_blueprint(estadisticas_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(health_bp)
