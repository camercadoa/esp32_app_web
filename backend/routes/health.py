from flask import Blueprint, jsonify
from config.database import get_connection
from datetime import datetime
import pytz

health_bp = Blueprint('health', __name__, url_prefix='/api/health')


@health_bp.route('/', methods=['GET'])
def health_check():
    """Verifica el estado general del servidor y la base de datos."""
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT 1 AS ok")
            result = cursor.fetchone()
        conexion.close()

        # Si devuelve 1, la DB está operativa
        db_status = "OK" if result and result.get("ok") == 1 else "ERROR"

    except Exception as e:
        db_status = "ERROR"
        print("❌ Error al verificar base de datos:", e)

    # Hora actual en zona Colombia
    tz_col = pytz.timezone("America/Bogota")
    now = datetime.now(tz_col).strftime("%Y-%m-%d %H:%M:%S")

    # Respuesta JSON
    return jsonify({
        "status": "OK",
        "database": db_status,
        "timestamp": now,
        "service": "ControlMotor API",
        "version": "1.0.0"
    }), 200
