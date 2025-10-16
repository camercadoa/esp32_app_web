#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ============================================================================
// CONFIGURACIÓN WiFi - ¡CAMBIAR ESTOS VALORES!
// ============================================================================
const char *ssid = "TU_NOMBRE_WIFI";
const char *password = "TU_PASSWORD_WIFI";

// URL de tu API
const char* apiURL = "http://TU_IP_LOCAL:5000/api/acciones";

// ============================================================================
// CONFIGURACIÓN LCD
// ============================================================================
int lcdColumnas = 16;
int lcdFilas = 2;
LiquidCrystal_I2C lcd(0x27, lcdColumnas, lcdFilas);

// ============================================================================
// CONFIGURACIÓN MOTOR (PWM)
// ============================================================================
int motor1Pin1 = 12;
int motor1Pin2 = 14;
int enable1Pin = 13;
int dutyCycle = 200; // Velocidad del motor (0-255)

// ============================================================================
// CONFIGURACIÓN BOTONES Y LEDS
// ============================================================================
int btnMotorOn = 27;
int btnMotorOff = 26;
int btnLedVerde = 25;
int btnLedRojo = 33;

int ledVerdePin = 15;
int ledRojoPin = 2;

// Estados
bool motorEncendido = false;
bool ledVerdeEncendido = false;
bool ledRojoEncendido = false;

// Estados anteriores de botones
bool lastBtnOnState = LOW;
bool lastBtnOffState = LOW;
bool lastBtnLedVerde = LOW;
bool lastBtnLedRojo = LOW;

unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

// Usuario por defecto (admin tiene id=1)
int usuarioId = 1;

// ============================================================================
// FUNCIONES WiFi
// ============================================================================
void conectarWiFi()
{
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Conectando WiFi");

    WiFi.begin(ssid, password);

    int intentos = 0;
    while (WiFi.status() != WL_CONNECTED && intentos < 20)
    {
        delay(500);
        Serial.print(".");
        lcd.setCursor(intentos % 16, 1);
        lcd.print(".");
        intentos++;
    }

    if (WiFi.status() == WL_CONNECTED)
    {
        Serial.println("\n✅ WiFi conectado");
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());

        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("WiFi OK");
        lcd.setCursor(0, 1);
        lcd.print(WiFi.localIP());
        delay(2000);
    }
    else
    {
        Serial.println("\n⚠️ No se pudo conectar a WiFi");
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("WiFi Error");
        lcd.setCursor(0, 1);
        lcd.print("Modo offline");
        delay(2000);
    }
}

void enviarAccionAPI(String dispositivo, String accion)
{
    if (WiFi.status() != WL_CONNECTED)
    {
        Serial.println("⚠️ Sin conexión WiFi - no se envió a API");
        return;
    }

    HTTPClient http;
    http.begin(apiURL);
    http.addHeader("Content-Type", "application/json");

    // Construir JSON
    String jsonData = "{";
    jsonData += "\"usuario_id\":" + String(usuarioId) + ",";
    jsonData += "\"dispositivo\":\"" + dispositivo + "\",";
    jsonData += "\"accion\":\"" + accion + "\"";
    jsonData += "}";

    Serial.println("📡 Enviando a API: " + jsonData);

    int httpResponseCode = http.POST(jsonData);

    if (httpResponseCode > 0)
    {
        String response = http.getString();
        Serial.println("✅ Respuesta API (" + String(httpResponseCode) + "): " + response);
    }
    else
    {
        Serial.print("❌ Error HTTP: ");
        Serial.println(httpResponseCode);
    }

    http.end();
}

// ============================================================================
// FUNCIONES DE CONTROL
// ============================================================================
void mostrarEstado(const char *componente, const char *estado)
{
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(componente);
    lcd.setCursor(0, 1);
    lcd.print(estado);
}

void motorOn()
{
    digitalWrite(motor1Pin1, HIGH);
    digitalWrite(motor1Pin2, LOW);
    analogWrite(enable1Pin, dutyCycle);

    motorEncendido = true;
    mostrarEstado("Motor", "ON");
    Serial.println("MOTOR:ENCENDER");
    enviarAccionAPI("MOTOR", "ENCENDER");
}

void motorOff()
{
    digitalWrite(motor1Pin1, LOW);
    digitalWrite(motor1Pin2, LOW);
    analogWrite(enable1Pin, 0);

    motorEncendido = false;
    mostrarEstado("Motor", "OFF");
    Serial.println("MOTOR:APAGAR");
    enviarAccionAPI("MOTOR", "APAGAR");
}

void toggleLedVerde()
{
    ledVerdeEncendido = !ledVerdeEncendido;
    digitalWrite(ledVerdePin, ledVerdeEncendido ? HIGH : LOW);

    mostrarEstado("Led Verde", ledVerdeEncendido ? "ON" : "OFF");
    Serial.println(ledVerdeEncendido ? "LED_VERDE:ENCENDER" : "LED_VERDE:APAGAR");
    enviarAccionAPI("LED_VERDE", ledVerdeEncendido ? "ENCENDER" : "APAGAR");
}

void toggleLedRojo()
{
    ledRojoEncendido = !ledRojoEncendido;
    digitalWrite(ledRojoPin, ledRojoEncendido ? HIGH : LOW);

    mostrarEstado("Led Rojo", ledRojoEncendido ? "ON" : "OFF");
    Serial.println(ledRojoEncendido ? "LED_ROJO:ENCENDER" : "LED_ROJO:APAGAR");
    enviarAccionAPI("LED_ROJO", ledRojoEncendido ? "ENCENDER" : "APAGAR");
}

// ============================================================================
// SETUP
// ============================================================================
void setup()
{
    Serial.begin(9600);

    // Inicializar LCD
    lcd.init();
    lcd.backlight();

    // Conectar WiFi
    conectarWiFi();

    mostrarEstado("Sistema Listo", "Pulsa un boton");

    // Configurar pines
    pinMode(motor1Pin1, OUTPUT);
    pinMode(motor1Pin2, OUTPUT);
    pinMode(enable1Pin, OUTPUT);
    pinMode(ledVerdePin, OUTPUT);
    pinMode(ledRojoPin, OUTPUT);
    pinMode(btnMotorOn, INPUT);
    pinMode(btnMotorOff, INPUT);
    pinMode(btnLedVerde, INPUT);
    pinMode(btnLedRojo, INPUT);

    // Inicializar apagados
    digitalWrite(ledVerdePin, LOW);
    digitalWrite(ledRojoPin, LOW);
    digitalWrite(motor1Pin1, LOW);
    digitalWrite(motor1Pin2, LOW);
}

// ============================================================================
// LOOP
// ============================================================================
void loop()
{
    // Verificar conexión WiFi cada 30 segundos
    static unsigned long lastWiFiCheck = 0;
    if (millis() - lastWiFiCheck > 30000)
    {
        if (WiFi.status() != WL_CONNECTED)
        {
            Serial.println("⚠️ WiFi desconectado, reconectando...");
            conectarWiFi();
        }
        lastWiFiCheck = millis();
    }

    // Control desde Serial (compatible con app de escritorio)
    if (Serial.available() > 0)
    {
        String comando = Serial.readStringUntil('\n');
        comando.trim();

        if (comando == "ON")
        {
            motorOn();
        }
        else if (comando == "OFF")
        {
            motorOff();
        }
        else if (comando == "LED_VERDE_ON")
        {
            if (!ledVerdeEncendido)
                toggleLedVerde();
        }
        else if (comando == "LED_VERDE_OFF")
        {
            if (ledVerdeEncendido)
                toggleLedVerde();
        }
        else if (comando == "LED_ROJO_ON")
        {
            if (!ledRojoEncendido)
                toggleLedRojo();
        }
        else if (comando == "LED_ROJO_OFF")
        {
            if (ledRojoEncendido)
                toggleLedRojo();
        }
    }

    // Leer botones físicos
    bool currentBtnOnState = digitalRead(btnMotorOn);
    bool currentBtnOffState = digitalRead(btnMotorOff);
    bool currentBtnLedVerde = digitalRead(btnLedVerde);
    bool currentBtnLedRojo = digitalRead(btnLedRojo);

    // Motor ON
    if (currentBtnOnState == LOW && lastBtnOnState == HIGH)
    {
        if ((millis() - lastDebounceTime) > debounceDelay)
        {
            if (!motorEncendido)
            {
                motorOn();
            }
            lastDebounceTime = millis();
        }
    }

    // Motor OFF
    if (currentBtnOffState == LOW && lastBtnOffState == HIGH)
    {
        if ((millis() - lastDebounceTime) > debounceDelay)
        {
            if (motorEncendido)
            {
                motorOff();
            }
            lastDebounceTime = millis();
        }
    }

    // LED Verde
    if (currentBtnLedVerde == HIGH && lastBtnLedVerde == LOW)
    {
        toggleLedVerde();
        delay(300);
    }

    // LED Rojo
    if (currentBtnLedRojo == HIGH && lastBtnLedRojo == LOW)
    {
        toggleLedRojo();
        delay(300);
    }

    // Guardar estados
    lastBtnOnState = currentBtnOnState;
    lastBtnOffState = currentBtnOffState;
    lastBtnLedVerde = currentBtnLedVerde;
    lastBtnLedRojo = currentBtnLedRojo;

    delay(10);
}