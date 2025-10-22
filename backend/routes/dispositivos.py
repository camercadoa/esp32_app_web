from flask import Blueprint, request, jsonify
from config.database import get_connection

dispositivos_bp = Blueprint(
    'dispositivos', __name__, url_prefix='/api/dispositivos')


# ------------------------------------------------------------
# Obtener todos los dispositivos
# ------------------------------------------------------------
@dispositivos_bp.route('/', methods=['GET'])
def listar_dispositivos():
    """
    Devuelve la lista de dispositivos registrados en la base de datos.
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT id, nombre, tipo, estado_actual, descripcion, creado_en
                FROM dispositivos
                ORDER BY id ASC
            """)
            dispositivos = cursor.fetchall()

        return jsonify({
            "success": True,
            "total": len(dispositivos),
            "dispositivos": dispositivos
        }), 200

    except Exception as e:
        print("Error al listar dispositivos:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# Obtener un dispositivo específico
# ------------------------------------------------------------
@dispositivos_bp.route('/<int:dispositivo_id>', methods=['GET'])
def obtener_dispositivo(dispositivo_id):
    """
    Devuelve la información de un dispositivo por su ID.
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT id, nombre, tipo, estado_actual, descripcion, creado_en
                FROM dispositivos
                WHERE id = %s
            """, (dispositivo_id,))
            dispositivo = cursor.fetchone()

        if not dispositivo:
            return jsonify({"error": "Dispositivo no encontrado"}), 404

        return jsonify({"success": True, "dispositivo": dispositivo}), 200

    except Exception as e:
        print("Error al obtener dispositivo:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# Actualizar el estado manualmente
# ------------------------------------------------------------
@dispositivos_bp.route('/<int:dispositivo_id>/estado', methods=['PUT'])
def actualizar_estado(dispositivo_id):
    """
    Permite actualizar manualmente el estado_actual de un dispositivo.
    """
    data = request.get_json()
    nuevo_estado = data.get('estado_actual')

    if nuevo_estado not in ['ENCENDIDO', 'APAGADO']:
        return jsonify({"error": "Estado inválido. Use 'ENCENDIDO' o 'APAGADO'."}), 400

    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            # Verificar si existe
            cursor.execute(
                "SELECT * FROM dispositivos WHERE id = %s", (dispositivo_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Dispositivo no encontrado"}), 404

            # Actualizar estado
            cursor.execute("""
                UPDATE dispositivos
                SET estado_actual = %s
                WHERE id = %s
            """, (nuevo_estado, dispositivo_id))
            conexion.commit()

        return jsonify({
            "success": True,
            "message": f"Estado del dispositivo actualizado a {nuevo_estado}"
        }), 200

    except Exception as e:
        print("Error al actualizar estado del dispositivo:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()
