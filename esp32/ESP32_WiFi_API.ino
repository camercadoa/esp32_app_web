#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Keypad.h>

// ============================================================================
// CONFIGURACIÓN WiFi - ¡CAMBIAR ESTOS VALORES!
// ============================================================================
const char *ssid = "TU_NOMBRE_WIFI";
const char *password = "TU_PASSWORD_WIFI";

// URL de tu API
const char *apiURL = "http://TU_IP_LOCAL:5000/api/acciones";

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
// CONFIGURACIÓN TECLADO MATRICIAL
// ============================================================================
const byte FILAS = 4;
const byte COLUMNAS = 4;
char teclas[FILAS][COLUMNAS] = {
    {'1', '2', '3', 'A'},
    {'4', '5', '6', 'B'},
    {'7', '8', '9', 'C'},
    {'*', '0', '#', 'D'}};

// Pines:
//      F1=D19, F2=D18, F3=D5, F4=TX2(17)
//      C1=RX2(16), C2=D4, C3=D2, C4=D15
byte pinesFilas[FILAS] = {19, 18, 5, 17};
byte pinesColumnas[COLUMNAS] = {16, 4, 2, 15};

Keypad teclado = Keypad(makeKeymap(teclas), pinesFilas, pinesColumnas, FILAS, COLUMNAS);

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
        Serial.println("\nWiFi conectado");
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
        Serial.println("\nNo se pudo conectar a WiFi");
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
        Serial.println("Sin conexión WiFi - no se envió a API");
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
        Serial.println("Respuesta API (" + String(httpResponseCode) + "): " + response);
    }
    else
    {
        Serial.print("Error HTTP: ");
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
// FUNCIONES DEL TECLADO
// ============================================================================
int menuActual = 0; // 0 = principal, 1=LED verde, 2=LED rojo, 3=motor, 4=estados
bool enSubmenu = false;

void mostrarMenuPrincipal()
{
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("1:Led V 2:Led R");
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
    if (tecla)
    {
        Serial.print("Tecla presionada: ");
        Serial.println(tecla);

        if (!enSubmenu)
        {
            if (tecla >= '1' && tecla <= '4')
            {
                menuActual = tecla - '0';
                enSubmenu = true;

                if (menuActual == 1)
                    mostrarSubmenu("LED Verde");
                else if (menuActual == 2)
                    mostrarSubmenu("LED Rojo");
                else if (menuActual == 3)
                    mostrarSubmenu("Motor");
                else if (menuActual == 4)
                {
                    lcd.clear();
                    lcd.print("Consultando BD...");
                    // Aquí en Fase 3 haremos la consulta a la API
                }
            }
        }
        else
        {
            // Submenús de acción
            if (tecla == '1')
            {
                if (menuActual == 1)
                {
                    if (!ledVerdeEncendido)
                        toggleLedVerde();
                }
                else if (menuActual == 2)
                {
                    if (!ledRojoEncendido)
                        toggleLedRojo();
                }
                else if (menuActual == 3)
                {
                    if (!motorEncendido)
                        motorOn();
                }
            }
            else if (tecla == '2')
            {
                if (menuActual == 1)
                {
                    if (ledVerdeEncendido)
                        toggleLedVerde();
                }
                else if (menuActual == 2)
                {
                    if (ledRojoEncendido)
                        toggleLedRojo();
                }
                else if (menuActual == 3)
                {
                    if (motorEncendido)
                        motorOff();
                }
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
                // Volver al menú principal
                enSubmenu = false;
                mostrarMenuPrincipal();
            }
        }
    }
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
            Serial.println("WiFi desconectado, reconectando...");
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