from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el navegador

# Configuración de la BD (Aiven)
DB_CONFIG = {
    "host": "sistema-control-123-sistemadecontrol123.i.aivencloud.com",
    "user": "avnadmin",
    "password": "AVNS_OHpXdLOCWg3oB4AvSbA",
    "database": "defaultdb",
    "port": 14718,
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "ssl": {"ssl": {}},
    "connect_timeout": 30
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

# ============================================================================
# ENDPOINT: Registrar acción desde ESP32
# ============================================================================
@app.route('/api/acciones', methods=['POST'])
def registrar_accion():
    try:
        data = request.get_json()
        
        usuario_id = data.get('usuario_id', 1)  # Por defecto admin
        dispositivo = data.get('dispositivo')
        accion = data.get('accion')
        
        if not dispositivo or not accion:
            return jsonify({"error": "Faltan datos"}), 400
        
        # Validar valores permitidos
        dispositivos_validos = ['MOTOR', 'LED_VERDE', 'LED_ROJO']
        acciones_validas = ['ENCENDER', 'APAGAR']
        
        if dispositivo not in dispositivos_validos or accion not in acciones_validas:
            return jsonify({"error": "Valores inválidos"}), 400
        
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO acciones (usuario_id, dispositivo, accion)
                    VALUES (%s, %s, %s)
                """, (usuario_id, dispositivo, accion))
            conexion.commit()
            
            return jsonify({
                "success": True,
                "message": "Acción registrada correctamente"
            }), 201
            
        finally:
            conexion.close()
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ENDPOINT: Obtener todas las acciones
# ============================================================================
@app.route('/api/acciones', methods=['GET'])
def obtener_acciones():
    try:
        limite = request.args.get('limite', 100, type=int)
        usuario_id = request.args.get('usuario_id', type=int)
        
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                query = """
                    SELECT a.id, a.dispositivo, a.accion, a.fecha_hora, 
                           u.username as usuario
                    FROM acciones a
                    JOIN usuarios u ON a.usuario_id = u.id
                """
                
                if usuario_id:
                    query += " WHERE a.usuario_id = %s"
                    cursor.execute(query + " ORDER BY a.fecha_hora DESC LIMIT %s", 
                                 (usuario_id, limite))
                else:
                    cursor.execute(query + " ORDER BY a.fecha_hora DESC LIMIT %s", 
                                 (limite,))
                
                acciones = cursor.fetchall()
                
                # Convertir datetime a string
                tz_colombia = pytz.timezone("America/Bogota")
                for accion in acciones:
                    if isinstance(accion['fecha_hora'], datetime):
                        fecha_utc = accion['fecha_hora'].replace(tzinfo=pytz.UTC)
                        fecha_local = fecha_utc.astimezone(tz_colombia)
                        accion['fecha_hora'] = fecha_local.strftime("%Y-%m-%d %H:%M:%S")
                
                return jsonify({
                    "success": True,
                    "total": len(acciones),
                    "acciones": acciones
                }), 200
                
        finally:
            conexion.close()
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ENDPOINT: Estadísticas del sistema
# ============================================================================
@app.route('/api/estadisticas', methods=['GET'])
def obtener_estadisticas():
    try:
        conexion = get_connection()
        try:
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
                
                # Última acción
                cursor.execute("""
                    SELECT dispositivo, accion, fecha_hora
                    FROM acciones
                    ORDER BY fecha_hora DESC
                    LIMIT 1
                """)
                ultima_accion = cursor.fetchone()
                
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
                
        finally:
            conexion.close()
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ENDPOINT: Estado actual del sistema
# ============================================================================
@app.route('/api/estado', methods=['GET'])
def obtener_estado():
    try:
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                # Obtener última acción de cada dispositivo
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
                
                return jsonify({
                    "success": True,
                    "estado": estado
                }), 200
                
        finally:
            conexion.close()
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ENDPOINT: Health check
# ============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        conexion = get_connection()
        conexion.close()
        return jsonify({
            "success": True,
            "message": "API funcionando correctamente",
            "database": "Conectada"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error en la conexión",
            "error": str(e)
        }), 500

# ============================================================================
# INICIAR SERVIDOR
# ============================================================================
if __name__ == '__main__':
    print("🚀 API iniciada en http://0.0.0.0:5000")
    print("📡 Endpoints disponibles:")
    print("   - POST /api/acciones (registrar acción)")
    print("   - GET  /api/acciones (obtener historial)")
    print("   - GET  /api/estadisticas (estadísticas)")
    print("   - GET  /api/estado (estado actual)")
    print("   - GET  /api/health (verificar conexión)")
    
    app.run(host='0.0.0.0', port=5000, debug=True)