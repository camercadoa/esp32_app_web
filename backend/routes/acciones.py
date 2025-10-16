from flask import Blueprint, request, jsonify
from config.database import get_connection
from datetime import datetime
import pytz

acciones_bp = Blueprint('acciones', __name__)


@acciones_bp.route('/api/acciones', methods=['POST'])
def registrar_accion():
    try:
        data = request.get_json()
        usuario_id = data.get('usuario_id', 1)
        dispositivo = data.get('dispositivo')
        accion = data.get('accion')

        if not dispositivo or not accion:
            return jsonify({"error": "Faltan datos"}), 400

        dispositivos_validos = ['MOTOR', 'LED_VERDE', 'LED_ROJO']
        acciones_validas = ['ENCENDER', 'APAGAR']

        if dispositivo not in dispositivos_validos or accion not in acciones_validas:
            return jsonify({"error": "Valores inválidos"}), 400

        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO acciones (usuario_id, dispositivo, accion)
                VALUES (%s, %s, %s)
            """, (usuario_id, dispositivo, accion))
        conexion.commit()
        conexion.close()

        return jsonify({"success": True, "message": "Acción registrada correctamente"}), 201

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@acciones_bp.route('/api/acciones', methods=['GET'])
def obtener_acciones():
    try:
        limite = request.args.get('limite', 100, type=int)
        usuario_id = request.args.get('usuario_id', type=int)

        conexion = get_connection()
        with conexion.cursor() as cursor:
            query = """
                SELECT a.id, a.dispositivo, a.accion, a.fecha_hora,
                    u.username as usuario
                FROM acciones a
                JOIN usuarios u ON a.usuario_id = u.id
            """

            if usuario_id:
                query += " WHERE a.usuario_id = %s ORDER BY a.fecha_hora DESC LIMIT %s"
                cursor.execute(query, (usuario_id, limite))
            else:
                query += " ORDER BY a.fecha_hora DESC LIMIT %s"
                cursor.execute(query, (limite,))

            acciones = cursor.fetchall()

        conexion.close()

        # Convertir fecha a zona horaria de Colombia
        tz_colombia = pytz.timezone("America/Bogota")
        for accion in acciones:
            if isinstance(accion['fecha_hora'], datetime):
                fecha_utc = accion['fecha_hora'].replace(tzinfo=pytz.UTC)
                fecha_local = fecha_utc.astimezone(tz_colombia)
                accion['fecha_hora'] = fecha_local.strftime(
                    "%Y-%m-%d %H:%M:%S")

        return jsonify({
            "success": True,
            "total": len(acciones),
            "acciones": acciones
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
