#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "DukeOpen";
const char* mqttServer = "10.194.90.55";
const int mqttPort = 1883;
const char* mqttUser = "test";
const char* mqttPassword = "test";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid);
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi.");

  client.setServer(mqttServer, mqttPort);
  
  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");
    if (client.connect("ESP32Client", mqttUser, mqttPassword )) {
      Serial.println("MQTT connected");  
    } else {
      Serial.print("failed with state ");
      Serial.print(client.state());
      delay(2000);
    }
  }
  client.publish("/plant", "Hello from ESP32");
}

void loop() {
  client.publish("/plant", "Hello from ESP32");
  delay(1000);
  client.loop();

}
