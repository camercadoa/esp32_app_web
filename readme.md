# 🎛️ Sistema de Control Motor DC y LEDs con ESP32

[![Python](https://img.shields.io/badge/Python-33.4%25-blue?logo=python)]
[![HTML](https://img.shields.io/badge/HTML-30.4%25-red?logo=html5)]
[![JavaScript](https://img.shields.io/badge/JavaScript-25.9%25-yellow?logo=javascript)]
[![CSS](https://img.shields.io/badge/CSS-10.3%25-blueviolet?logo=css3)]

---

## 📋 Descripción del Proyecto

Sistema completo de monitoreo y control que integra hardware y software:

- **ESP32** conectado vía WiFi para controlar un motor DC y dos LEDs.
- **API REST** en Flask, que gestiona todas las acciones y el acceso a la base de datos.
- **Aplicación Web** moderna para visualizar y controlar el sistema en tiempo real.
- **Base de datos MySQL** de prueba en la nube (Aiven).

Este sistema es ideal para prácticas de IoT, automatización y monitoreo remoto.

---

## 📦 Tecnologías Principales

| Componente           | Tecnología         |
|----------------------|-------------------|
| Backend/API          | Python (Flask)    |
| Frontend Web         | HTML, CSS, JS     |
| Microcontrolador     | ESP32 (Arduino C++)|
| Base de datos        | MySQL (Aiven)     |

---

## 🚀 Instalación

### 1️⃣ Configuración del entorno Python

```bash
python -m venv venv
# Activar el entorno
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 2️⃣ Configuración del ESP32

**Requisitos:**

- Arduino IDE y ESP32 configurado
- Bibliotecas: `WiFi.h`, `HTTPClient.h`, `Wire.h`, `LiquidCrystal_I2C`

**Pasos:**

1. Abre `esp32/ESP32_WiFi_API.ino` en Arduino IDE.
2. Cambia las credenciales WiFi:

   ```cpp
   const char* ssid = "TU_NOMBRE_WIFI";
   const char* password = "TU_PASSWORD_WIFI";
   ```

3. Encuentra la IP de tu computadora (usa `ipconfig` o `ifconfig`).
4. Cambia la URL de la API:

   ```cpp
   const char* apiURL = "http://TU_IP_LOCAL:5000/api/acciones";
   ```

5. Sube el código al ESP32.

---

## 🎮 Uso del Sistema

### 1️⃣ Inicia la API

```bash
python backend/app.py
```

Verás:

```bash
🚀 API iniciada en http://0.0.0.0:5000
📡 Endpoints disponibles...
```

### 2️⃣ Abre la página en el navegador

- Por defecto se carga en la ruta `http://127.0.0.1:5000/`

> **IMPORTANTE:**
> Si la web no carga datos, edita `backend\static\js\main.js` (línea 1):
>
> ```javascript
> const API_URL = 'http://localhost:5000/api';
> ```
>
> Cambia `localhost` por la IP de tu PC si accedes desde otro dispositivo.

### 3️⃣ Enciende el ESP32

El ESP32:

- Se conecta a WiFi
- Muestra su IP en el LCD
- Envía cada acción a la API
- La API registra en la base de datos

---

## 🔌 Conexiones del Hardware

| Elemento         | GPIO        |
|------------------|------------|
| Motor Pin 1      | 12         |
| Motor Pin 2      | 14         |
| Enable (PWM)     | 13         |
| LED Verde        | 15         |
| LED Rojo         | 2          |
| Botón Motor ON   | 27         |
| Botón Motor OFF  | 26         |
| Botón LED Verde  | 25         |
| Botón LED Rojo   | 33         |
| LCD I2C SDA      | 21         |
| LCD I2C SCL      | 22         |
| Dirección I2C    | 0x27       |

---

## 🌐 Endpoints de la API

- **Registrar Acción**

  ```http
  POST /api/acciones
  Content-Type: application/json

  {
      "usuario_id": 1,
      "dispositivo": "MOTOR",
      "accion": "ENCENDER"
  }
  ```

- **Obtener Historial**

  ```http
  GET /api/acciones?limite=100&usuario_id=1
  ```

- **Obtener Estadísticas**

  ```http
  GET /api/estadisticas
  ```

- **Estado Actual**

  ```http
  GET /api/estado
  ```

- **Health Check**

  ```http
  GET /api/health
  ```

---

## 📊 Características de la Aplicación Web

- ✅ Monitoreo en tiempo real
- ✅ Visualización de estado actual por dispositivo
- ✅ Historial completo con búsqueda instantánea
- ✅ Estadísticas de uso
- ✅ Indicador de conexión con la API
- ✅ Interfaz responsive y moderna

---

## 🐛 Solución de Problemas

### El ESP32 no se conecta a WiFi

- Verifica las credenciales y el rango de la red
- Usa solo redes 2.4GHz

### La API no responde

- Revisa firewall y acceso al puerto 5000
- Comprueba la conexión a Internet para Aiven

### La web no carga datos

- Revisa consola de navegador (F12)
- Comprueba que la API esté activa
- Desactiva CORS temporalmente o usa extensión "CORS Unblock"

### El ESP32 no guarda en BD

- Revisa la URL de la API en el código
- Verifica la IP y errores en el Monitor Serial
- Prueba la API con Postman o curl

---

## 🔒 Seguridad

⚠️ **Advertencia:** Este proyecto es para propósitos educativos. Para producción:

- Cambia credenciales de la base de datos y agrégalos a un archivo `.env`
- Implementa autenticación JWT en la API
- Usa HTTPS
- Valida y sanitiza todas las entradas
- Implementa control de acceso y rate limiting

**Comandos útiles:**

```bash
# Ver puertos en uso (Windows)
netstat -ano | findstr :5000

# Probar API desde consola
curl http://localhost:5000/api/health

# Ver IP de la computadora
ipconfig  # Windows
ifconfig  # Linux/Mac
```

---

¿Tienes dudas o sugerencias? ¡Abre un issue!
