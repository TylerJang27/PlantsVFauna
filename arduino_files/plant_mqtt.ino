#include <Adafruit_MLX90640.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>

char* ssid = "DukeOpen";
int device_id = 1;
const char* mqttServer = "plantsvfauna.colab.duke.edu";
const int mqttPort = 1883;
const char* mqttUser = "test";
const char* mqttPassword = "test";
int counter = 0;

const char* MESSAGE_TYPE_PEST = "pest";
const char* MESSAGE_TYPE_REPORT = "report";
const char* MESSAGE_TYPE_POWER_ON = "power_on";
const char* MESSAGE_TYPE_POWER_OFF = "power_off";
const char* MESSAGE_TYPE_BATTERY = "battery";
const char* MESSAGE_TYPE_STARTUP = "startup";
const char* MESSAGE_TYPE_SHUTDOWN = "shutdown";

const char* MESSAGE_KEY_TYPE = "type";
const char* MESSAGE_KEY_DEVICE = "device_id";
const char* MESSAGE_KEY_DESCRIPTION = "description";
const char* MESSAGE_KEY_BATTERY = "battery";
const char* MESSAGE_KEY_TIME = "time";



WiFiClient espClient;
PubSubClient client(espClient);
DynamicJsonDocument doc(16384);
char test_buffer[16384];

Adafruit_MLX90640 mlx;
float frame[32 * 24]; // buffer for full frame of temperatures
//int buffer_thermal[768];

//low range of the sensor (this will be blue on the screen)
int MINTEMP = 20;

//high range of the sensor (this will be red on the screen)
int MAXTEMP = 35;

////the colors we will be using
//const uint16_t camColors[] = {0x480F,
//0x400F,0x400F,0x400F,0x4010,0x3810,0x3810,0x3810,0x3810,0x3010,0x3010,
//0x3010,0x2810,0x2810,0x2810,0x2810,0x2010,0x2010,0x2010,0x1810,0x1810,
//0x1811,0x1811,0x1011,0x1011,0x1011,0x0811,0x0811,0x0811,0x0011,0x0011,
//0x0011,0x0011,0x0011,0x0031,0x0031,0x0051,0x0072,0x0072,0x0092,0x00B2,
//0x00B2,0x00D2,0x00F2,0x00F2,0x0112,0x0132,0x0152,0x0152,0x0172,0x0192,
//0x0192,0x01B2,0x01D2,0x01F3,0x01F3,0x0213,0x0233,0x0253,0x0253,0x0273,
//0x0293,0x02B3,0x02D3,0x02D3,0x02F3,0x0313,0x0333,0x0333,0x0353,0x0373,
//0x0394,0x03B4,0x03D4,0x03D4,0x03F4,0x0414,0x0434,0x0454,0x0474,0x0474,
//0x0494,0x04B4,0x04D4,0x04F4,0x0514,0x0534,0x0534,0x0554,0x0554,0x0574,
//0x0574,0x0573,0x0573,0x0573,0x0572,0x0572,0x0572,0x0571,0x0591,0x0591,
//0x0590,0x0590,0x058F,0x058F,0x058F,0x058E,0x05AE,0x05AE,0x05AD,0x05AD,
//0x05AD,0x05AC,0x05AC,0x05AB,0x05CB,0x05CB,0x05CA,0x05CA,0x05CA,0x05C9,
//0x05C9,0x05C8,0x05E8,0x05E8,0x05E7,0x05E7,0x05E6,0x05E6,0x05E6,0x05E5,
//0x05E5,0x0604,0x0604,0x0604,0x0603,0x0603,0x0602,0x0602,0x0601,0x0621,
//0x0621,0x0620,0x0620,0x0620,0x0620,0x0E20,0x0E20,0x0E40,0x1640,0x1640,
//0x1E40,0x1E40,0x2640,0x2640,0x2E40,0x2E60,0x3660,0x3660,0x3E60,0x3E60,
//0x3E60,0x4660,0x4660,0x4E60,0x4E80,0x5680,0x5680,0x5E80,0x5E80,0x6680,
//0x6680,0x6E80,0x6EA0,0x76A0,0x76A0,0x7EA0,0x7EA0,0x86A0,0x86A0,0x8EA0,
//0x8EC0,0x96C0,0x96C0,0x9EC0,0x9EC0,0xA6C0,0xAEC0,0xAEC0,0xB6E0,0xB6E0,
//0xBEE0,0xBEE0,0xC6E0,0xC6E0,0xCEE0,0xCEE0,0xD6E0,0xD700,0xDF00,0xDEE0,
//0xDEC0,0xDEA0,0xDE80,0xDE80,0xE660,0xE640,0xE620,0xE600,0xE5E0,0xE5C0,
//0xE5A0,0xE580,0xE560,0xE540,0xE520,0xE500,0xE4E0,0xE4C0,0xE4A0,0xE480,
//0xE460,0xEC40,0xEC20,0xEC00,0xEBE0,0xEBC0,0xEBA0,0xEB80,0xEB60,0xEB40,
//0xEB20,0xEB00,0xEAE0,0xEAC0,0xEAA0,0xEA80,0xEA60,0xEA40,0xF220,0xF200,
//0xF1E0,0xF1C0,0xF1A0,0xF180,0xF160,0xF140,0xF100,0xF0E0,0xF0C0,0xF0A0,
//0xF080,0xF060,0xF040,0xF020,0xF800,};

uint16_t displayPixelWidth, displayPixelHeight;

void setup() {
  Serial.begin(9600);
  pinMode(33, INPUT);
  WiFi.begin(ssid);
  while (WiFi.status() != WL_CONNECTED) {
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

  Serial.println("Adafruit MLX90640 Camera");
  if (! mlx.begin(MLX90640_I2CADDR_DEFAULT, &Wire)) {
    Serial.println("Not found");
  }
  Serial.println("Found Adafruit MLX90640");

  Serial.print("Serial number: ");
  Serial.print(mlx.serialNumber[0], HEX);
  Serial.print(mlx.serialNumber[1], HEX);
  Serial.println(mlx.serialNumber[2], HEX);

  mlx.setMode(MLX90640_CHESS);
  mlx.setResolution(MLX90640_ADC_18BIT);
  mlx.setRefreshRate(MLX90640_8_HZ);
  Wire.setClock(1000000); // max 1 MHz

}


void attachMeta(DynamicJsonDocument doc, int message_type) {
  int battery = 55;  // TODO: MEASURE THIS

  doc[MESSAGE_KEY_DEVICE] = device_id;
  doc[MESSAGE_KEY_BATTERY] = battery;
  char* message_type_msg = "";
  if (message_type == 1) {
    message_type_msg = (char*)MESSAGE_TYPE_PEST;  // TODO: CHANGE TO REPORT AS NECESSARY
  } else if (message_type == 2) {
    message_type_msg = (char*)MESSAGE_TYPE_REPORT;
  } else if (message_type == 3) {
    message_type_msg = (char*)MESSAGE_TYPE_STARTUP;
  } else if (message_type == 4) {
    message_type_msg = (char*)MESSAGE_TYPE_SHUTDOWN;
  }
  doc[MESSAGE_KEY_TYPE] = message_type_msg;
 
  doc[MESSAGE_KEY_TIME] = "";  // TODO: CHANGE TO PARSE TIME
}

DynamicJsonDocument parseJson(char msg[]) {
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, msg);

  const char* message_type = doc[MESSAGE_KEY_TYPE];
  int in_device_id = doc[MESSAGE_KEY_DEVICE];

  String in_message_type, compare_message_type1, compare_message_type2;
  in_message_type = String(message_type);
  compare_message_type1 = String(MESSAGE_TYPE_POWER_ON);
  compare_message_type2 = String(MESSAGE_TYPE_POWER_OFF);

  if (in_device_id == device_id) {
    if (in_message_type == compare_message_type1) {
      Serial.println("TURN ON REMOTE");
      // TODO: IMPLEMENT/TOGGLE BOOLEAN
    } else if (in_message_type == compare_message_type2) {
      Serial.println("TURN OFF REMOTE");
      // TODO: IMPLEMENT/TOGGLE BOOLEAN
    }
  }
}

void readImageAndSendMessage() {
  // json pre metadata
  attachMeta(doc, 1);

  for (uint8_t h = 0; h < 24; h++) {
    char row_index[20];
    sprintf(row_index, "camValue%u", h);
    doc[row_index];
    for (uint8_t w = 0; w < 32; w++) {
      float t = frame[h * 32 + w];

      if (t > MAXTEMP) {
        t = MAXTEMP;
      }
      else if (t < MINTEMP) {
        t = MINTEMP;
      }


      uint8_t colorIndex = map(t, MINTEMP, MAXTEMP, 0, 255);

      colorIndex = constrain(colorIndex, 0, 255);


      doc[row_index][w] = colorIndex;
    }
  }

  size_t n = serializeJson(doc, test_buffer);
  client.beginPublish("/plant", n, false);
  for (int i = 0; i < n; i++) {
    client.write(test_buffer[i]);
  }
  client.endPublish();

  // TODO: CLEANUP doc AND REMOVE IMAGE AND FIELDS
}

void loop() {
  if (counter == 0) { // TODO: ADD MORE BOOLEANS AND LOGIC FOR ON STATUS

    readImageAndSendMessage();

    uint32_t timestamp = millis();
    if (mlx.getFrame(frame) != 0) {
      Serial.println("Failed");
      return;
    }
    //    int colorTemp;


    counter++;
    Serial.print((millis() - timestamp) / 2); Serial.println(" ms per frame (2 frames per display)");
    Serial.print(2000.0 / (millis() - timestamp)); Serial.println(" FPS (2 frames per display)");

    //
    delay(100);
    client.loop();
  }
}