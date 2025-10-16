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
    """Crea y retorna una conexión a la base de datos."""
    return pymysql.connect(**DB_CONFIG)
