#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>

#define WIFI_SSID "coldfire"
#define WIFI_PASSWORD "1234567890"

// Replace with your server address
const char* serverName = "http://your-server-address/api";

unsigned long previousMillis = 0;
const long interval = 10000; // Interval to send message (10 seconds)

// Stability monitoring variables
unsigned long uptimeMillis = 0;
unsigned int successfulSends = 0;
unsigned int failedSends = 0;

bool isConnected = false;

void setup() {
  Serial.begin(921600);  // Initialize serial communication at 921600 baud
  pinMode(LED_BUILTIN, OUTPUT);  // Set the LED pin as output

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);  // Start WiFi connection

  Serial.println("Starting...");  // Print starting message
}

void sendMessage() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);

    int httpResponseCode = http.GET();

    if (httpResponseCode == HTTP_CODE_OK) { // Check if the response code is 200 (HTTP OK)
      String response = http.getString();
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      successfulSends++;
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
      failedSends++;
    }
    
    http.end();
  } else {
    Serial.println("WiFi Disconnected. Reconnecting...");
    failedSends++;
  }
}

void loop() {
  // Check the Wi-Fi connection status
  if (WiFi.status() == WL_CONNECTED) {
    if (!isConnected) {
      Serial.println("Connected to WiFi");  // Message when connected
      digitalWrite(LED_BUILTIN, HIGH);  // Turn on the LED
      isConnected = true;
    }
  } else {
    if (isConnected) {
      Serial.println("Disconnected from WiFi");  // Message when disconnected
      digitalWrite(LED_BUILTIN, LOW);  // Turn off the LED
      isConnected = false;
    }
  }

  unsigned long currentMillis = millis();

  // Check if it's time to send a message
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    sendMessage();
  }

  // Monitor device stability (e.g., uptime)
  uptimeMillis = millis();
  Serial.print("Uptime (seconds): ");
  Serial.println(uptimeMillis / 1000);
  Serial.print("Successful Sends: ");
  Serial.println(successfulSends);
  Serial.print("Failed Sends: ");
  Serial.println(failedSends);
  delay(1000);  // Adjust as needed
}
