from flask import Blueprint, jsonify
from config.database import get_connection
from datetime import datetime
import pytz

estadisticas_bp = Blueprint('estadisticas', __name__, url_prefix='/api/estadisticas')

# ------------------------------------------------------------
# Indicadores generales (cards del dashboard)
# ------------------------------------------------------------
@estadisticas_bp.route('/indicadores', methods=['GET'])
def indicadores_generales():
    """
    Devuelve métricas principales para el tablero:
    - Total de acciones
    - Porcentaje encender/apagar
    - Dispositivo más usado
    - Usuarios activos últimas 24h
    - Sesiones iniciadas esta semana
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            # Total de acciones
            cursor.execute("SELECT COUNT(*) AS total_acciones FROM acciones")
            total_acciones = cursor.fetchone()["total_acciones"]

            # Porcentaje encender/apagar
            cursor.execute("""
                SELECT accion, COUNT(*) AS cantidad
                FROM acciones
                GROUP BY accion
            """)
            acciones_tipo = cursor.fetchall()
            encender = next((a["cantidad"] for a in acciones_tipo if a["accion"] == "ENCENDER"), 0)
            apagar = next((a["cantidad"] for a in acciones_tipo if a["accion"] == "APAGAR"), 0)

            porcentaje_enc = round((encender / total_acciones) * 100, 2) if total_acciones else 0
            porcentaje_apg = round((apagar / total_acciones) * 100, 2) if total_acciones else 0

            # Dispositivo más usado
            cursor.execute("""
                SELECT d.nombre AS nombre_dispositivo, COUNT(a.id) AS total
                FROM acciones a
                JOIN dispositivos d ON a.dispositivo_id = d.id
                GROUP BY d.nombre
                ORDER BY total DESC
                LIMIT 1
            """)
            mas_usado = cursor.fetchone()
            dispositivo_mas_usado = mas_usado["nombre_dispositivo"] if mas_usado else "N/A"

            # Usuarios activos últimas 24h
            cursor.execute("""
                SELECT COUNT(DISTINCT usuario_id) AS activos
                FROM acciones
                WHERE fecha_hora >= NOW() - INTERVAL 1 DAY
            """)
            usuarios_activos = cursor.fetchone()["activos"]

            # Sesiones iniciadas esta semana
            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM sesiones
                WHERE WEEK(fecha_inicio) = WEEK(NOW())
            """)
            sesiones_semana = cursor.fetchone()["total"]

        return jsonify({
            "success": True,
            "indicadores": {
                "total_acciones": total_acciones,
                "porcentaje_encender": porcentaje_enc,
                "porcentaje_apagar": porcentaje_apg,
                "dispositivo_mas_usado": dispositivo_mas_usado,
                "usuarios_activos_24h": usuarios_activos,
                "sesiones_semana": sesiones_semana
            }
        }), 200

    except Exception as e:
        print("Error en indicadores:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# 1. Historial diario de acciones
# ------------------------------------------------------------
@estadisticas_bp.route('/acciones-diarias', methods=['GET'])
def acciones_diarias():
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT DATE(fecha_hora) AS fecha, COUNT(*) AS total
                FROM acciones
                GROUP BY DATE(fecha_hora)
                ORDER BY fecha ASC
            """)
            data = cursor.fetchall()

        fechas = [str(row["fecha"]) for row in data]
        totales = [row["total"] for row in data]

        return jsonify({"labels": fechas, "data": totales}), 200

    except Exception as e:
        print("Error en acciones_diarias:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# 2. Distribución de acciones por dispositivo
# ------------------------------------------------------------
@estadisticas_bp.route('/acciones-por-dispositivo', methods=['GET'])
def acciones_por_dispositivo():
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT d.nombre AS dispositivo, COUNT(a.id) AS total
                FROM acciones a
                JOIN dispositivos d ON a.dispositivo_id = d.id
                GROUP BY d.nombre
            """)
            data = cursor.fetchall()

        dispositivos = [row["dispositivo"] for row in data]
        totales = [row["total"] for row in data]

        return jsonify({"labels": dispositivos, "data": totales}), 200

    except Exception as e:
        print("Error en acciones_por_dispositivo:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# 3. Proporción de encender vs apagar
# ------------------------------------------------------------
@estadisticas_bp.route('/acciones-por-tipo', methods=['GET'])
def acciones_por_tipo():
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT accion AS tipo, COUNT(*) AS total
                FROM acciones
                GROUP BY accion
            """)
            data = cursor.fetchall()

        tipos = [row["tipo"] for row in data]
        totales = [row["total"] for row in data]

        return jsonify({"labels": tipos, "data": totales}), 200

    except Exception as e:
        print("Error en acciones_por_tipo:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# 4. Acciones por usuario (ranking)
# ------------------------------------------------------------
@estadisticas_bp.route('/acciones-por-usuario', methods=['GET'])
def acciones_por_usuario():
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT u.nombre AS usuario, COUNT(a.id) AS total
                FROM acciones a
                JOIN usuarios u ON a.usuario_id = u.id
                GROUP BY u.nombre
                ORDER BY total DESC
            """)
            data = cursor.fetchall()

        usuarios = [row["usuario"] for row in data]
        totales = [row["total"] for row in data]

        return jsonify({"labels": usuarios, "data": totales}), 200

    except Exception as e:
        print("Error en acciones_por_usuario:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# 5. Última acción registrada
# ------------------------------------------------------------
@estadisticas_bp.route('/ultima-accion', methods=['GET'])
def ultima_accion():
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT a.accion, d.nombre AS nombre_dispositivo, u.nombre AS usuario, a.fecha_hora
                FROM acciones a
                JOIN dispositivos d ON a.dispositivo_id = d.id
                JOIN usuarios u ON a.usuario_id = u.id
                ORDER BY a.fecha_hora DESC
                LIMIT 1
            """)
            ultima = cursor.fetchone()

        if not ultima:
            return jsonify({"success": False, "message": "No hay acciones registradas"}), 404

        tz_col = pytz.timezone("America/Bogota")
        fecha_local = ultima["fecha_hora"].replace(tzinfo=pytz.UTC).astimezone(tz_col)
        ultima["fecha_hora"] = fecha_local.strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({"success": True, "ultima_accion": ultima}), 200

    except Exception as e:
        print("Error en ultima_accion:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()
