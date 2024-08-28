#include <Arduino.h>
#include <WiFi.h>

#define WIFI_SSID "coldfire"
#define WIFI_PASSWORD "1234567890"

void setup(){
  Serial.begin(921600);  // Initialize serial communication at 921600 baud
  pinMode(LED_BUILTIN, OUTPUT);  // Set the LED pin as output

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);  // Start WiFi connection

  Serial.println("Starting...");  // Print starting message
}

bool isConnected = false;

void loop(){
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
  
  delay(1000);  // Delay to avoid flooding the serial monitor
}
