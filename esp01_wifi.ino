#include <ESP8266WiFi.h>

#ifndef STASSID
#define STASSID "***********"
#define STAPSK "***********"
#endif

const char* ssid = STASSID;
const char* password = STAPSK;

WiFiServer server(80);

void setup() {
  delay(5000);
  pinMode(0, OUTPUT);
  pinMode(2, OUTPUT);
  digitalWrite(0, LOW);
  digitalWrite(2, LOW);
  // Serial.begin(9600);
  // Serial.print("Connecting to ");
  // Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();

  WiFi.begin(ssid,password);

  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    // Serial.print(".");
  }

  // Serial.println("ESP-01 is connected to the ssid");
  // Serial.println(WiFi.localIP());
  server.begin();
  delay(1000);
}

void loop() {
  WiFiClient client;
  client = server.available();

  if (client == 1){
    String request = client.readStringUntil('\n');
    client.flush();
    // Serial.println(request);

    if (request.indexOf("open") != -1){
      digitalWrite(0, HIGH);
      delay(5000);
      digitalWrite(0, LOW);
      delay(1000);
      digitalWrite(2, HIGH);
      delay(5000);
      digitalWrite(2, LOW);
      // Serial.println("Openning door");
    }
    // Serial.print("Client Disconnected");
    // Serial.println(" ");
  }
}
