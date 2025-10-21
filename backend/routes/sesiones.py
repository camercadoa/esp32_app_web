from flask import Blueprint, jsonify, request
from config.database import get_connection
from datetime import datetime
import pytz

sesiones_bp = Blueprint('sesiones', __name__, url_prefix='/api/sesiones')


# ------------------------------------------------------------
# 🟩 Registrar inicio de sesión
# ------------------------------------------------------------
@sesiones_bp.route('/iniciar', methods=['POST'])
def iniciar_sesion():
    """
    Registra una nueva sesión en la tabla 'sesiones'.
    Se espera un JSON con: usuario_id e ip_origen.
    """
    try:
        data = request.get_json()
        usuario_id = data.get("usuario_id")
        ip_origen = data.get("ip_origen", request.remote_addr)

        if not usuario_id:
            return jsonify({"error": "El campo 'usuario_id' es obligatorio"}), 400

        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sesiones (usuario_id, ip_origen)
                VALUES (%s, %s)
            """, (usuario_id, ip_origen))
            conexion.commit()

        return jsonify({"success": True, "message": "Sesión iniciada correctamente"}), 201

    except Exception as e:
        print("❌ Error en iniciar_sesion:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# 🟥 Registrar cierre de sesión
# ------------------------------------------------------------
@sesiones_bp.route('/cerrar', methods=['POST'])
def cerrar_sesion():
    """
    Marca la sesión más reciente del usuario como cerrada (fecha_fin).
    Se espera un JSON con: usuario_id
    """
    try:
        data = request.get_json()
        usuario_id = data.get("usuario_id")

        if not usuario_id:
            return jsonify({"error": "El campo 'usuario_id' es obligatorio"}), 400

        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE sesiones
                SET fecha_fin = NOW()
                WHERE usuario_id = %s AND fecha_fin IS NULL
                ORDER BY fecha_inicio DESC
                LIMIT 1
            """, (usuario_id,))
            conexion.commit()

        return jsonify({"success": True, "message": "Sesión cerrada correctamente"}), 200

    except Exception as e:
        print("❌ Error en cerrar_sesion:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# 🟦 Consultar sesiones activas
# ------------------------------------------------------------
@sesiones_bp.route('/activas', methods=['GET'])
def sesiones_activas():
    """
    Devuelve los usuarios que tienen una sesión sin fecha_fin (activa).
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT s.id, u.nombre, u.username, s.fecha_inicio, s.ip_origen
                FROM sesiones s
                JOIN usuarios u ON s.usuario_id = u.id
                WHERE s.fecha_fin IS NULL
                ORDER BY s.fecha_inicio DESC
            """)
            sesiones = cursor.fetchall()

        tz_col = pytz.timezone("America/Bogota")
        for s in sesiones:
            s["fecha_inicio"] = s["fecha_inicio"].replace(
                tzinfo=pytz.UTC).astimezone(tz_col).strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({"success": True, "sesiones_activas": sesiones}), 200

    except Exception as e:
        print("❌ Error en sesiones_activas:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# 📋 Consultar historial de sesiones
# ------------------------------------------------------------
@sesiones_bp.route('/historial', methods=['GET'])
def historial_sesiones():
    """
    Devuelve el historial completo de sesiones, cerradas y activas.
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT s.id, u.nombre, u.username, s.fecha_inicio, s.fecha_fin, s.ip_origen
                FROM sesiones s
                JOIN usuarios u ON s.usuario_id = u.id
                ORDER BY s.fecha_inicio DESC
            """)
            sesiones = cursor.fetchall()

        tz_col = pytz.timezone("America/Bogota")
        for s in sesiones:
            s["fecha_inicio"] = s["fecha_inicio"].replace(
                tzinfo=pytz.UTC).astimezone(tz_col).strftime("%Y-%m-%d %H:%M:%S")
            if s["fecha_fin"]:
                s["fecha_fin"] = s["fecha_fin"].replace(tzinfo=pytz.UTC).astimezone(
                    tz_col).strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({"success": True, "historial": sesiones}), 200

    except Exception as e:
        print("❌ Error en historial_sesiones:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()
