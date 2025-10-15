# 🎛️ Sistema de Control Motor DC y LEDs con ESP32

## 📋 Descripción del Proyecto

Sistema completo de monitoreo y control que integra:
- **ESP32** conectado a WiFi que controla un motor DC y 2 LEDs
- **API REST** en Flask que gestiona la base de datos
- **Aplicación Web** para visualizar el historial en tiempo real
- **Base de datos MySQL** en Aiven (nube)

---

## 🚀 Instalación

### 1️⃣ Configurar el entorno Python

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ Configurar la Base de Datos

La base de datos ya está configurada en Aiven. Si necesitas recrear las tablas:

```bash
python init_db.py
```

Esto creará:
- Tabla `usuarios` (con usuario admin/1234)
- Tabla `acciones` (historial de eventos)

### 3️⃣ Configurar el ESP32

**Requisitos:**
- Arduino IDE instalado
- ESP32 configurado en Arduino IDE
- Bibliotecas necesarias:
  - `WiFi.h` (incluida en ESP32)
  - `HTTPClient.h` (incluida en ESP32)
  - `Wire.h`
  - `LiquidCrystal_I2C`

**Pasos:**

1. Abre el archivo `ESP32_WiFi_API.ino` en Arduino IDE

2. **Cambia las credenciales WiFi:**
   ```cpp
   const char* ssid = "TU_NOMBRE_WIFI";        // ⚠️ Tu red WiFi
   const char* password = "TU_PASSWORD_WIFI";   // ⚠️ Tu contraseña
   ```

3. **Encuentra la IP de tu computadora:**
   
   En Windows (CMD):
   ```bash
   ipconfig
   ```
   Busca "Dirección IPv4" (ejemplo: 192.168.1.100)
   
   En Linux/Mac (Terminal):
   ```bash
   ifconfig
   # o
   ip addr show
   ```

4. **Cambia la URL de la API:**
   ```cpp
   const char* apiURL = "http://192.168.1.100:5000/api/acciones";
   ```
   Reemplaza `192.168.1.100` con TU IP

5. Sube el código al ESP32

---

## 🎮 Uso del Sistema

### 1️⃣ Iniciar la API

```bash
python api.py
```

Verás:
```
🚀 API iniciada en http://0.0.0.0:5000
📡 Endpoints disponibles:
   - POST /api/acciones (registrar acción)
   - GET  /api/acciones (obtener historial)
   - GET  /api/estadisticas (estadísticas)
   - GET  /api/estado (estado actual)
   - GET  /api/health (verificar conexión)
```

### 2️⃣ Abrir la Aplicación Web

1. Abre el archivo `index.html` en tu navegador

2. O para un servidor local:
   ```bash
   # Python 3
   python -m http.server 8000
   ```
   Luego ve a: `http://localhost:8000`

3. **IMPORTANTE:** Si la página no carga datos, edita `index.html` línea 308:
   ```javascript
   const API_URL = 'http://localhost:5000/api';
   ```
   Cambia `localhost` por la IP de tu computadora si es necesario

### 3️⃣ Encender el ESP32

El ESP32 automáticamente:
1. Se conecta a WiFi
2. Muestra su IP en el LCD
3. Envía cada acción a la API
4. Actualiza la base de datos

---

## 🔌 Conexiones del Hardware

### Motor DC
- Motor Pin 1 → GPIO 12
- Motor Pin 2 → GPIO 14
- Enable (PWM) → GPIO 13

### LEDs
- LED Verde → GPIO 15
- LED Rojo → GPIO 2

### Botones
- Botón Motor ON → GPIO 27
- Botón Motor OFF → GPIO 26
- Botón LED Verde → GPIO 25
- Botón LED Rojo → GPIO 33

### LCD I2C
- SDA → GPIO 21
- SCL → GPIO 22
- Dirección I2C: 0x27

---

## 🌐 Endpoints de la API

### 1. Registrar Acción
```http
POST /api/acciones
Content-Type: application/json

{
    "usuario_id": 1,
    "dispositivo": "MOTOR",
    "accion": "ENCENDER"
}
```

**Dispositivos válidos:** `MOTOR`, `LED_VERDE`, `LED_ROJO`  
**Acciones válidas:** `ENCENDER`, `APAGAR`

### 2. Obtener Historial
```http
GET /api/acciones?limite=100&usuario_id=1
```

### 3. Obtener Estadísticas
```http
GET /api/estadisticas
```

### 4. Estado Actual
```http
GET /api/estado
```

### 5. Health Check
```http
GET /api/health
```

---

## 📊 Características de la Aplicación Web

✅ **Monitoreo en tiempo real** (actualización cada 5 segundos)  
✅ **Visualización del estado actual** de cada dispositivo  
✅ **Historial completo** con búsqueda en tiempo real  
✅ **Estadísticas** de uso por dispositivo  
✅ **Indicador de conexión** con la API  
✅ **Diseño responsive** (funciona en móviles)  
✅ **Interfaz moderna** con animaciones

---

## 🐛 Solución de Problemas

### El ESP32 no se conecta a WiFi
- ✅ Verifica las credenciales WiFi
- ✅ Asegúrate que el ESP32 esté en rango
- ✅ Verifica que la red sea 2.4GHz (el ESP32 no soporta 5GHz)

### La API no responde
- ✅ Verifica que Python esté ejecutándose: `python api.py`
- ✅ Revisa el firewall (debe permitir puerto 5000)
- ✅ Verifica la conexión a Internet (para Aiven)

### La aplicación web no carga datos
- ✅ Abre la consola del navegador (F12) para ver errores
- ✅ Verifica que la API esté corriendo
- ✅ Cambia `localhost` por la IP real en `index.html`
- ✅ Desactiva CORS temporalmente o usa la extensión "CORS Unblock"

### El ESP32 envía pero no se guarda en BD
- ✅ Revisa la URL de la API en el código del ESP32
- ✅ Verifica que la IP sea correcta
- ✅ Revisa el Monitor Serial para ver errores HTTP
- ✅ Prueba la API con Postman o curl primero

---

## 📱 Capturas de Pantalla

La aplicación web muestra:

1. **Barra de estado** con indicador de conexión
2. **Tarjetas de dispositivos** con estado en tiempo real
3. **Tabla de historial** con búsqueda
4. **Estadísticas** de uso

---

## 🔒 Seguridad

⚠️ **IMPORTANTE:** Este proyecto es para desarrollo/educación. Para producción:

- Cambia las credenciales de la base de datos
- Implementa autenticación JWT en la API
- Usa HTTPS en lugar de HTTP
- Valida todas las entradas
- Implementa rate limiting

---

## 👥 Créditos

Proyecto desarrollado como parte del curso de sistemas embebidos.  
Base de datos: Aiven MySQL  
Framework web: Flask + HTML/CSS/JS  
Hardware: ESP32, Motor DC, LEDs, LCD I2C

---

## 📝 Notas Adicionales

- La aplicación de escritorio PyQt6 sigue funcionando normalmente
- Puedes usar ambas interfaces simultáneamente
- Los datos se sincronizan automáticamente
- La zona horaria está configurada para Colombia (America/Bogota)

---

## 🆘 Soporte

Si tienes problemas:

1. Revisa el Monitor Serial del ESP32
2. Revisa la consola de la API (Python)
3. Revisa la consola del navegador (F12)
4. Verifica que todos los servicios estén corriendo

**Comandos útiles para diagnóstico:**

```bash
# Ver puertos en uso (Windows)
netstat -ano | findstr :5000

# Probar API desde consola
curl http://localhost:5000/api/health

# Ver IP de la computadora
ipconfig  # Windows
ifconfig  # Linux/Mac
```