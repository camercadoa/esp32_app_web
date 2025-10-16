from flask import Blueprint, jsonify
from config.database import get_connection
from datetime import datetime
import pytz

estadisticas_bp = Blueprint('estadisticas', __name__)

@estadisticas_bp.route('/api/estadisticas', methods=['GET'])
def obtener_estadisticas():
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            # Total de acciones
            cursor.execute("SELECT COUNT(*) as total FROM acciones")
            total = cursor.fetchone()['total']

            # Acciones por dispositivo
            cursor.execute("""
                SELECT dispositivo, COUNT(*) as cantidad
                FROM acciones
                GROUP BY dispositivo
            """)
            por_dispositivo = cursor.fetchall()

            # Acciones por tipo
            cursor.execute("""
                SELECT accion, COUNT(*) as cantidad
                FROM acciones
                GROUP BY accion
            """)
            por_accion = cursor.fetchall()

            # Última acción registrada
            cursor.execute("""
                SELECT dispositivo, accion, fecha_hora
                FROM acciones
                ORDER BY fecha_hora DESC
                LIMIT 1
            """)
            ultima_accion = cursor.fetchone()

        conexion.close()

        # Convertir fecha a hora local
        if ultima_accion and isinstance(ultima_accion['fecha_hora'], datetime):
            tz_colombia = pytz.timezone("America/Bogota")
            fecha_utc = ultima_accion['fecha_hora'].replace(tzinfo=pytz.UTC)
            fecha_local = fecha_utc.astimezone(tz_colombia)
            ultima_accion['fecha_hora'] = fecha_local.strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "success": True,
            "estadisticas": {
                "total_acciones": total,
                "por_dispositivo": por_dispositivo,
                "por_accion": por_accion,
                "ultima_accion": ultima_accion
            }
        }), 200

    except Exception as e:
        print(f"Error en /api/estadisticas: {e}")
        return jsonify({"error": str(e)}), 500
