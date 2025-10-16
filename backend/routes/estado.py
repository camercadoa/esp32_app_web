from flask import Blueprint, jsonify
from config.database import get_connection

estado_bp = Blueprint('estado', __name__)

@estado_bp.route('/api/estado', methods=['GET'])
def obtener_estado():
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            estado = {}
            dispositivos = ['MOTOR', 'LED_VERDE', 'LED_ROJO']

            for dispositivo in dispositivos:
                cursor.execute("""
                    SELECT accion, fecha_hora
                    FROM acciones
                    WHERE dispositivo = %s
                    ORDER BY fecha_hora DESC
                    LIMIT 1
                """, (dispositivo,))
                resultado = cursor.fetchone()

                if resultado:
                    estado[dispositivo.lower()] = {
                        "estado": resultado['accion'],
                        "activo": resultado['accion'] == 'ENCENDER'
                    }
                else:
                    estado[dispositivo.lower()] = {
                        "estado": "DESCONOCIDO",
                        "activo": False
                    }

        conexion.close()

        return jsonify({
            "success": True,
            "estado": estado
        }), 200

    except Exception as e:
        print(f"Error en /api/estado: {e}")
        return jsonify({"error": str(e)}), 500
