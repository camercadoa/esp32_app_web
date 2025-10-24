#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Keypad.h>
#include <ArduinoJson.h>

// ============================================================================
// CONFIGURACIÓN WiFi
// ============================================================================
const char *ssid = "Camilo";
const char *password = "redmin13";

// URL base de tu API
const char *apiBaseURL = "http://10.110.150.231:5000/api";

// ============================================================================
// CONFIGURACIÓN LCD
// ============================================================================
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ============================================================================
// CONFIGURACIÓN MOTOR Y LEDS
// ============================================================================
int motor1Pin1 = 12;
int motor1Pin2 = 14;
int enable1Pin = 13;
int dutyCycle = 200;

int btnMotorOn = 27;
int btnMotorOff = 26;
int btnLedVerde = 25;
int btnLedRojo = 33;
int ledVerdePin = 2;
int ledRojoPin = 32;

bool motorEncendido = false;
bool ledVerdeEncendido = false;
bool ledRojoEncendido = false;

unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

// IDs de dispositivos
const int DISP_MOTOR_ID = 1;
const int DISP_LED_VERDE_ID = 2;
const int DISP_LED_ROJO_ID = 3;

// Usuario activo
int usuarioId = 1;
String nombreUsuario = "Desconocido";

// ============================================================================
// CONFIGURACIÓN TECLADO MATRICIAL
// ============================================================================
const byte FILAS = 4;
const byte COLUMNAS = 4;
char teclas[FILAS][COLUMNAS] = {
    {'1', '2', '3', 'A'},
    {'4', '5', '6', 'B'},
    {'7', '8', '9', 'C'},
    {'*', '0', '#', 'D'}};

byte pinesFilas[FILAS] = {23, 19, 18, 5};
byte pinesColumnas[COLUMNAS] = {17, 16, 4, 15};
Keypad teclado = Keypad(makeKeymap(teclas), pinesFilas, pinesColumnas, FILAS, COLUMNAS);

// ============================================================================
// FUNCIONES WiFi y API
// ============================================================================
void mostrarEstado(const char *linea1, const char *linea2)
{
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(linea1);
    lcd.setCursor(0, 1);
    lcd.print(linea2);
}

void conectarWiFi()
{
    lcd.clear();
    lcd.print("Conectando...");
    WiFi.begin(ssid, password);

    int intentos = 0;
    while (WiFi.status() != WL_CONNECTED && intentos < 20)
    {
        delay(500);
        lcd.setCursor(intentos % 16, 1);
        lcd.print(".");
        intentos++;
    }

    if (WiFi.status() == WL_CONNECTED)
    {
        lcd.clear();
        lcd.print("WiFi OK");
        lcd.setCursor(0, 1);
        lcd.print(WiFi.localIP());
        delay(1500);
    }
    else
    {
        lcd.clear();
        lcd.print("WiFi Error");
        lcd.setCursor(0, 1);
        lcd.print("Modo offline");
        delay(1500);
    }
}

// Obtener usuario activo desde la API
void obtenerUsuarioActivo()
{
    if (WiFi.status() != WL_CONNECTED)
        return;

    String url = String(apiBaseURL) + "/usuarios/activo";
    HTTPClient http;
    http.begin(url);
    int httpCode = http.GET();

    if (httpCode == 200)
    {
        String payload = http.getString();
        DynamicJsonDocument doc(512);
        DeserializationError err = deserializeJson(doc, payload);

        if (!err && doc["success"])
        {
            usuarioId = doc["usuario_activo"]["id"].as<int>();
            nombreUsuario = doc["usuario_activo"]["nombre"].as<String>();
            mostrarEstado("Usuario:", nombreUsuario.c_str());
            delay(2000);
        }
    }

    http.end();
}

// Enviar acción a la API
void enviarAccionAPI(int dispositivoId, String accion)
{
    if (WiFi.status() != WL_CONNECTED)
    {
        Serial.println("Sin conexión WiFi - no se envió a API");
        return;
    }

    String url = String(apiBaseURL) + "/acciones/registrar";
    HTTPClient http;
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{";
    jsonData += "\"usuario_id\":" + String(usuarioId) + ",";
    jsonData += "\"dispositivo_id\":" + String(dispositivoId) + ",";
    jsonData += "\"accion\":\"" + accion + "\"";
    jsonData += "}";

    int code = http.POST(jsonData);
    http.end();

    Serial.printf("POST %s -> %d\n", url.c_str(), code);
}

// ============================================================================
// FUNCIONES DE CONTROL
// ============================================================================
void motorOn()
{
    if (!motorEncendido)
    {
        digitalWrite(motor1Pin1, HIGH);
        digitalWrite(motor1Pin2, LOW);
        analogWrite(enable1Pin, dutyCycle);
        motorEncendido = true;
        mostrarEstado("Motor", "ON");
        enviarAccionAPI(DISP_MOTOR_ID, "ENCENDER");
    }
    else
    {
        mostrarEstado("Motor", "Ya esta ON");
    }
}

void motorOff()
{
    if (motorEncendido)
    {
        digitalWrite(motor1Pin1, LOW);
        digitalWrite(motor1Pin2, LOW);
        analogWrite(enable1Pin, 0);
        motorEncendido = false;
        mostrarEstado("Motor", "OFF");
        enviarAccionAPI(DISP_MOTOR_ID, "APAGAR");
    }
    else
    {
        mostrarEstado("Motor", "Ya esta OFF");
    }
}

void ledVerdeOn()
{
    if (!ledVerdeEncendido)
    {
        ledVerdeEncendido = true;
        digitalWrite(ledVerdePin, HIGH);
        mostrarEstado("LED Verde", "ON");
        enviarAccionAPI(DISP_LED_VERDE_ID, "ENCENDER");
    }
    else
        mostrarEstado("LED Verde", "Ya ON");
}

void ledVerdeOff()
{
    if (ledVerdeEncendido)
    {
        ledVerdeEncendido = false;
        digitalWrite(ledVerdePin, LOW);
        mostrarEstado("LED Verde", "OFF");
        enviarAccionAPI(DISP_LED_VERDE_ID, "APAGAR");
    }
    else
        mostrarEstado("LED Verde", "Ya OFF");
}

void ledRojoOn()
{
    if (!ledRojoEncendido)
    {
        ledRojoEncendido = true;
        digitalWrite(ledRojoPin, HIGH);
        mostrarEstado("LED Rojo", "ON");
        enviarAccionAPI(DISP_LED_ROJO_ID, "ENCENDER");
    }
    else
        mostrarEstado("LED Rojo", "Ya ON");
}

void ledRojoOff()
{
    if (ledRojoEncendido)
    {
        ledRojoEncendido = false;
        digitalWrite(ledRojoPin, LOW);
        mostrarEstado("LED Rojo", "OFF");
        enviarAccionAPI(DISP_LED_ROJO_ID, "APAGAR");
    }
    else
        mostrarEstado("LED Rojo", "Ya OFF");
}

// ============================================================================
// TECLADO
// ============================================================================
int menuActual = 0;
bool enSubmenu = false;

void mostrarMenuPrincipal()
{
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("1:LedV 2:LedR");
    lcd.setCursor(0, 1);
    lcd.print("3:Motor 4:BD");
}

void mostrarSubmenu(String nombre)
{
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(nombre);
    lcd.setCursor(0, 1);
    lcd.print("1:ON 2:OFF 3:EST");
}

void manejarTeclado()
{
    char tecla = teclado.getKey();
    if (!tecla)
        return;

    if (!enSubmenu)
    {
        if (tecla >= '1' && tecla <= '3')
        {
            menuActual = tecla - '0';
            enSubmenu = true;
            if (menuActual == 1)
                mostrarSubmenu("LED Verde");
            else if (menuActual == 2)
                mostrarSubmenu("LED Rojo");
            else if (menuActual == 3)
                mostrarSubmenu("Motor");
        }
    }
    else
    {
        if (tecla == '1')
        {
            if (menuActual == 1)
                ledVerdeOn();
            else if (menuActual == 2)
                ledRojoOn();
            else if (menuActual == 3)
                motorOn();
        }
        else if (tecla == '2')
        {
            if (menuActual == 1)
                ledVerdeOff();
            else if (menuActual == 2)
                ledRojoOff();
            else if (menuActual == 3)
                motorOff();
        }
        else if (tecla == '3')
        {
            lcd.clear();
            if (menuActual == 1)
                lcd.print(ledVerdeEncendido ? "LED V: ON" : "LED V: OFF");
            else if (menuActual == 2)
                lcd.print(ledRojoEncendido ? "LED R: ON" : "LED R: OFF");
            else if (menuActual == 3)
                lcd.print(motorEncendido ? "Motor: ON" : "Motor: OFF");
            delay(1500);
            mostrarSubmenu(menuActual == 1 ? "LED Verde" : menuActual == 2 ? "LED Rojo" : "Motor");
        }
        else if (tecla == 'D')
        {
            enSubmenu = false;
            mostrarMenuPrincipal();
        }
    }
}

// ============================================================================
// SETUP
// ============================================================================
void setup()
{
    Serial.begin(115200);
    lcd.init();
    lcd.backlight();

    pinMode(motor1Pin1, OUTPUT);
    pinMode(motor1Pin2, OUTPUT);
    pinMode(enable1Pin, OUTPUT);
    pinMode(ledVerdePin, OUTPUT);
    pinMode(ledRojoPin, OUTPUT);
    pinMode(btnMotorOn, INPUT);
    pinMode(btnMotorOff, INPUT);
    pinMode(btnLedVerde, INPUT);
    pinMode(btnLedRojo, INPUT);

    conectarWiFi();
    obtenerUsuarioActivo();

    mostrarEstado("Sistema Listo", "Pulsa tecla");
    mostrarMenuPrincipal();
}

// ============================================================================
// LOOP
// ============================================================================
void loop()
{
    // Actualizar usuario activo cada 30 seg
    static unsigned long lastUserCheck = 0;
    if (millis() - lastUserCheck > 30000)
    {
        obtenerUsuarioActivo();
        lastUserCheck = millis();
    }

    manejarTeclado();
}
