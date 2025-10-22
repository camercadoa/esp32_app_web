from flask import Blueprint, request, jsonify
from config.database import get_connection

acciones_bp = Blueprint('acciones', __name__, url_prefix='/api/acciones')


# ------------------------------------------------------------
# Registrar acción (ENCENDER / APAGAR)
# ------------------------------------------------------------
@acciones_bp.route('/registrar', methods=['POST'])
def registrar_accion():
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    dispositivo_id = data.get('dispositivo_id')
    accion = data.get('accion')

    if not all([usuario_id, dispositivo_id, accion]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            # Verificar estado actual del dispositivo
            cursor.execute(
                "SELECT estado_actual FROM dispositivos WHERE id = %s", (dispositivo_id,))
            dispositivo = cursor.fetchone()
            if not dispositivo:
                return jsonify({"error": "Dispositivo no encontrado"}), 404

            estado_actual = dispositivo['estado_actual']

            # Determinar si hay cambio de estado o no
            if accion == 'ENCENDER' and estado_actual == 'ENCENDIDO':
                resultado = 'SIN_CAMBIO'
                comentario = 'El dispositivo ya está ENCENDIDO'
            elif accion == 'APAGAR' and estado_actual == 'APAGADO':
                resultado = 'SIN_CAMBIO'
                comentario = 'El dispositivo ya está APAGADO'
            else:
                # Actualizar estado en tabla dispositivos
                nuevo_estado = 'ENCENDIDO' if accion == 'ENCENDER' else 'APAGADO'
                cursor.execute(
                    "UPDATE dispositivos SET estado_actual = %s WHERE id = %s",
                    (nuevo_estado, dispositivo_id)
                )
                resultado = 'OK'
                comentario = f'Dispositivo {nuevo_estado} correctamente'

            # Registrar acción
            cursor.execute("""
                INSERT INTO acciones (usuario_id, dispositivo_id, accion, resultado, comentario)
                VALUES (%s, %s, %s, %s, %s)
            """, (usuario_id, dispositivo_id, accion, resultado, comentario))

            connection.commit()

        return jsonify({
            "message": "Acción registrada correctamente",
            "resultado": resultado,
            "comentario": comentario
        }), 201

    except Exception as e:
        print("Error al registrar acción:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()


# ------------------------------------------------------------
# Consultar historial de acciones
# ------------------------------------------------------------
@acciones_bp.route('/historial', methods=['GET'])
def listar_acciones():
    """Devuelve el historial de acciones (opcionalmente filtrado por usuario o dispositivo)"""
    usuario_id = request.args.get('usuario_id')
    dispositivo_id = request.args.get('dispositivo_id')

    query = """
        SELECT a.id, u.username, d.nombre AS dispositivo, a.accion, a.resultado, a.comentario, a.fecha_hora
        FROM acciones a
        JOIN usuarios u ON a.usuario_id = u.id
        JOIN dispositivos d ON a.dispositivo_id = d.id
        WHERE 1=1
    """
    params = []

    if usuario_id:
        query += " AND a.usuario_id = %s"
        params.append(usuario_id)

    if dispositivo_id:
        query += " AND a.dispositivo_id = %s"
        params.append(dispositivo_id)

    query += " ORDER BY a.fecha_hora DESC LIMIT 50"

    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            acciones = cursor.fetchall()

        return jsonify(acciones), 200

    except Exception as e:
        print("Error al obtener historial:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()
