#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>

// Replace with your network credentials
const char* ssid = "Pie";
const char* password = "Napie001";

// Replace with your PHP server's IP or domain
const char* serverName = "http://172.20.10.4/mywebserver/index.php"; // Update this 
//"http://ip address machine/mywebserver/index.php"

// Create a web server on port 80
WebServer server(80);

// Variables to keep track of uptime
unsigned long startMillis;
unsigned long previousMillis = 0; // Stores last time uptime was sent
const long interval = 60000; // Interval to send uptime (1 minute = 60000 milliseconds)

// LED pin
const int ledPin = 2; // Change this if your LED is connected to a different pin

// Handle incoming messages
void handleIncomingMessage() {
    if (server.hasArg("message")) {
        String message = server.arg("message");
        Serial.println("Received message: " + message);
        server.send(200, "text/plain", "Message received: " + message);
    } else {
        server.send(400, "text/plain", "No message received");
    }
}

// Handle uptime request
void handleUptime() {
    unsigned long currentMillis = millis();
    unsigned long elapsedMillis = currentMillis - startMillis;
    unsigned long elapsedMinutes = elapsedMillis / 60000;

    String uptimeMessage = "Uptime: " + String(elapsedMinutes) + " minutes";
    server.send(200, "text/plain", uptimeMessage);
}

// Handle root request
void handleRoot() {
    server.send(200, "text/plain", "Welcome to the ESP32 Web Server!\n\nVisit /message to send a message.\nVisit /uptime to see uptime.");
}

// Function to send uptime to PHP server
void sendUptimeToServer(unsigned long uptimeMinutes) {
    if (WiFi.status() == WL_CONNECTED) { // Check WiFi connection status
        HTTPClient http;

        // Prepare URL
        http.begin(serverName);

        // Specify content-type header
        http.addHeader("Content-Type", "application/x-www-form-urlencoded");

        // Prepare POST data
        String postData = "uptime=" + String(uptimeMinutes);

        // Send POST request
        int httpResponseCode = http.POST(postData);

        // Debugging
        if (httpResponseCode > 0) {
            Serial.print("HTTP Response code: ");
            Serial.println(httpResponseCode);
        } else {
            Serial.print("Error on sending POST: ");
            Serial.println(httpResponseCode);
        }

        // Free resources
        http.end();
    } else {
        Serial.println("WiFi Disconnected. Cannot send uptime.");
    }
}

void setup() {
    // Initialize Serial Monitor
    Serial.begin(115200);

    // Initialize LED pin
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, LOW); // Ensure LED is off initially

    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to Wi-Fi");
    int attempts = 0; // Number of connection attempts

    while (WiFi.status() != WL_CONNECTED && attempts < 20) { // Limit attempts to avoid infinite loop
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        // Wi-Fi connected, turn on LED
        Serial.println("\nConnected to Wi-Fi");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());

        // Print the URL
        Serial.print("URL: http://");
        Serial.print(WiFi.localIP());
        Serial.println(); // Port 80 is default, so no need to specify

        // Turn on the LED
        digitalWrite(ledPin, HIGH);
    } else {
        // Wi-Fi connection failed, keep LED off
        Serial.println("\nFailed to connect to Wi-Fi");
        Serial.println("Please check your credentials and network.");
        while (true); // Halt execution if Wi-Fi connection fails
    }

    // Initialize the start time
    startMillis = millis();

    // Define the HTTP server's responses
    server.on("/", handleRoot);
    server.on("/message", handleIncomingMessage);
    server.on("/uptime", handleUptime);

    // Start the HTTP server
    server.begin();
    Serial.println("HTTP server started on port 80");
}

void loop() {
    // Handle incoming HTTP requests
    server.handleClient();

    // Get current time
    unsigned long currentMillis = millis();

    // Send uptime and Wi-Fi status every minute
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;

        // Calculate uptime in minutes
        unsigned long elapsedMillis = currentMillis - startMillis;
        unsigned long elapsedMinutes = elapsedMillis / 60000;

        // Print uptime to Serial Monitor
        Serial.print("Uptime: ");
        Serial.print(elapsedMinutes);
        Serial.println(" minutes");

        // Check and print Wi-Fi status
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("Wi-Fi Status: Connected");
            //Serial.print("IP Address: ");
            //Serial.println(WiFi.localIP());

            // Send uptime to PHP server
            sendUptimeToServer(elapsedMinutes);
        } else {
            Serial.println("Wi-Fi Status: Disconnected");
        }
    }

    // Check Wi-Fi status and update LED accordingly
    if (WiFi.status() == WL_CONNECTED) {
        digitalWrite(ledPin, HIGH); // Ensure LED is on when connected
    } else {
        digitalWrite(ledPin, LOW); // Ensure LED is off when disconnected
    }
}
