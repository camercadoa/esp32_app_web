from flask import Blueprint, jsonify
from config.database import get_connection

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health', methods=['GET'])
def health_check():
    try:
        conexion = get_connection()
        conexion.close()
        return jsonify({
            "success": True,
            "message": "API funcionando correctamente",
            "database": "Conectada"
        }), 200
    except Exception as e:
        print(f"Error en /api/health: {e}")
        return jsonify({
            "success": False,
            "message": "Error en la conexión a la base de datos",
            "error": str(e)
        }), 500
