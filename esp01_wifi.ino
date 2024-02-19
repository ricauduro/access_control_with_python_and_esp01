#include <ESP8266WiFi.h>

#ifndef STASSID
#define STASSID "<your network id>"
#define STAPSK "<your password>"
#endif

const char *ssid = STASSID;
const char *password = STAPSK;

WiFiServer server(80);

void setup()
{
  pinMode(0, OUTPUT);
  digitalWrite(0, HIGH);
  // Serial.begin(9600);
  // Serial.print("Connecting to ");
  // Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
  }

  // Serial.println("ESP-01 is connected to the ssid");
  // Serial.println(WiFi.localIP());
  server.begin();
  delay(1000);
}

void loop()
{
  WiFiClient client;
  client = server.available();

  if (client == 1)
  {
    String request = client.readStringUntil('\n');
    client.flush();
    // Serial.println(request);

    if (request.indexOf("open") != -1)
    {
      digitalWrite(0, LOW);
      delay(5000);
      digitalWrite(0, HIGH);
      // Serial.println("Openning door");
    }
    // Serial.print("Client Disconnected");
    // Serial.println(" ");
  }
}
