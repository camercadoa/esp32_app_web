import pymysql

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
    """Crea y retorna una conexión a la base de datos MySQL."""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        # print("✅ Conexión exitosa a la base de datos.")
        return connection
    except pymysql.MySQLError as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None


def create_tables():
    """Crea las tablas necesarias si no existen."""
    connection = get_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                nombre VARCHAR(100),
                rol ENUM('ADMIN', 'USUARIO') DEFAULT 'USUARIO',
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS dispositivos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL,
                tipo ENUM('MOTOR', 'LED') NOT NULL,
                estado_actual ENUM('ENCENDIDO', 'APAGADO') DEFAULT 'APAGADO',
                descripcion VARCHAR(255),
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS acciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                dispositivo_id INT NOT NULL,
                accion ENUM('ENCENDER', 'APAGAR') NOT NULL,
                resultado ENUM('OK', 'SIN_CAMBIO', 'ERROR') DEFAULT 'OK',
                comentario VARCHAR(255),
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (dispositivo_id) REFERENCES dispositivos(id)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sesiones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_fin TIMESTAMP NULL,
                ip_origen VARCHAR(100),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
            """)

            connection.commit()
            print("✅ Tablas verificadas/creadas correctamente.")

    except pymysql.MySQLError as e:
        print(f"Error al crear las tablas: {e}")

    finally:
        connection.close()


# Ejecutar la creación de tablas si se llama directamente el archivo
if __name__ == "__main__":
    create_tables()
