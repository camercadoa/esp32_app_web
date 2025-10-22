from flask import Blueprint, jsonify
from config.database import get_connection

estado_bp = Blueprint('estado', __name__, url_prefix='/api/estado')


# ------------------------------------------------------------
# Obtener el estado actual de todos los dispositivos
# ------------------------------------------------------------
@estado_bp.route('/', methods=['GET'])
def obtener_estado_general():
    """
    Devuelve el estado actual de todos los dispositivos registrados.
    Ejemplo de salida:
    {
        "motor": "ENCENDIDO",
        "led_verde": "APAGADO",
        "led_rojo": "ENCENDIDO"
    }
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT nombre, tipo, estado_actual
                FROM dispositivos
                ORDER BY id ASC
            """)
            dispositivos = cursor.fetchall()

        # Transformar resultado a un formato más legible
        estado = {}
        for d in dispositivos:
            clave = d['nombre'].lower().replace(" ", "_")
            estado[clave] = d['estado_actual']

        return jsonify({
            "success": True,
            "estado": estado
        }), 200

    except Exception as e:
        print("Error al obtener estado general:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# Obtener el estado de un dispositivo específico
# ------------------------------------------------------------
@estado_bp.route('/<int:dispositivo_id>', methods=['GET'])
def obtener_estado_dispositivo(dispositivo_id):
    """
    Devuelve el estado actual de un dispositivo específico.
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT id, nombre, estado_actual
                FROM dispositivos
                WHERE id = %s
            """, (dispositivo_id,))
            dispositivo = cursor.fetchone()

        if not dispositivo:
            return jsonify({"error": "Dispositivo no encontrado"}), 404

        return jsonify({
            "success": True,
            "dispositivo": dispositivo
        }), 200

    except Exception as e:
        print("Error al obtener estado del dispositivo:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()
