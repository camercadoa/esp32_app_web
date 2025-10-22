from flask import Blueprint, request, jsonify
from config.database import get_connection
import bcrypt
import jwt
from datetime import datetime, timedelta
import pytz

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')

# Clave secreta para firmar el JWT
SECRET_KEY = "clave_secreta_segura_esp32_api_2025"


# ------------------------------------------------------------
# Registrar nuevo usuario
# ------------------------------------------------------------
@usuarios_bp.route('/registro', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    nombre = data.get("nombre")
    rol = data.get("rol", "USUARIO")

    if not username or not password:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            # Verificar si ya existe
            cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({"error": "El usuario ya existe"}), 409

            # Encriptar contraseña
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Insertar usuario
            cursor.execute("""
                INSERT INTO usuarios (username, password, nombre, rol)
                VALUES (%s, %s, %s, %s)
            """, (username, hashed.decode('utf-8'), nombre, rol))
            conexion.commit()

        return jsonify({"success": True, "message": "Usuario registrado exitosamente"}), 201

    except Exception as e:
        print("Error en registro:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# Inicio de sesión
# ------------------------------------------------------------
@usuarios_bp.route('/login', methods=['POST'])
def login_usuario():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Faltan credenciales"}), 400

    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id, password, nombre FROM usuarios WHERE username = %s", (username,))
            user = cursor.fetchone()

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({"error": "Credenciales inválidas"}), 401

        # Generar token JWT (válido por 4 horas)
        token = jwt.encode({
            "usuario_id": user["id"],
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=4)
        }, SECRET_KEY, algorithm="HS256")

        # Registrar sesión en base de datos
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sesiones (usuario_id, ip_origen)
                VALUES (%s, %s)
            """, (user["id"], request.remote_addr))
            conexion.commit()

        return jsonify({
            "success": True,
            "token": token,
            "usuario": {
                "id": user["id"],
                "username": username,
                "nombre": user["nombre"]
            }
        }), 200

    except Exception as e:
        print("Error en login:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()


# ------------------------------------------------------------
# Consultar usuario activo más reciente
# (para mostrar en el LCD del ESP32)
# ------------------------------------------------------------
@usuarios_bp.route('/activo', methods=['GET'])
def obtener_usuario_activo():
    """
    Devuelve el nombre del último usuario que inició sesión.
    Esto se puede usar para mostrar en el LCD del ESP32.
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT u.nombre, u.username, s.fecha_inicio
                FROM sesiones s
                JOIN usuarios u ON s.usuario_id = u.id
                ORDER BY s.fecha_inicio DESC
                LIMIT 1
            """)
            sesion = cursor.fetchone()

        if not sesion:
            return jsonify({"success": False, "message": "No hay usuarios activos"}), 404

        # Convertir hora a Colombia
        tz_col = pytz.timezone("America/Bogota")
        fecha_local = sesion["fecha_inicio"].replace(tzinfo=pytz.UTC).astimezone(tz_col)
        sesion["fecha_inicio"] = fecha_local.strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "success": True,
            "usuario_activo": sesion
        }), 200

    except Exception as e:
        print("Error al obtener usuario activo:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conexion.close()
