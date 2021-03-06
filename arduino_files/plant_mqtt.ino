#include <ESP32Servo.h>
#include <analogWrite.h>
#include <ESP32Tone.h>
#include <ESP32PWM.h>

#include <Adafruit_MLX90640.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "pitches.h"

char* ssid = "DukeOpen";
//char* ssid = "TJ_DUMMY_1";
//char* passphrase = "00000000";
int device_id = 1;
bool remote_on = true;
const char* mqttServer = "plantsvfauna.colab.duke.edu";
const int mqttPort = 1883;
const char* mqttUser = "test";
const char* mqttPassword = "test";
int counter = 0;
const int DEBUG_LEVEL = 1;
const bool SOUND_ENABLED = true;

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

const char* MESSAGE_KEY_MINTEMP = "minTemp";
const char* MESSAGE_KEY_MAXTEMP = "maxTemp";
const char* MESSAGE_KEY_COUNT = "count";
const char* MESSAGE_KEY_COLORINDEX = "colorIndex";


unsigned long previousTime = 0;

int maxTempThresh = 35;
int minTempThresh = 19;
int colorIndexThresh = 90;
int countThresh = 50;

const char* willPayload = "{\"type\": \"shutdown\", \"device_id\": 1, \"description\": \"will message\", \"battery\": 10}";
bool willRetain = true;
int willQos = 1;


int melody[] = {
  NOTE_D5, NOTE_DS5, NOTE_E5, NOTE_F5,
  NOTE_FS5, NOTE_G5, NOTE_GS5, NOTE_A5,
  NOTE_AS5, NOTE_B5, NOTE_C6, NOTE_CS6, NOTE_D6, NOTE_DS6,
  NOTE_E6, NOTE_F6, NOTE_F6, NOTE_F6,

  NOTE_E6, NOTE_DS6, NOTE_D6,
  NOTE_CS6, NOTE_C6, NOTE_B5, NOTE_AS5, NOTE_A5, NOTE_GS5, NOTE_G5, NOTE_FS5,      //29               //8
  NOTE_F5, NOTE_E5, NOTE_DS5, NOTE_D5, END
};

int lightON = 32;
bool state = LOW;
int speed = 90;
int blink = 0;

WiFiClient espClient;
PubSubClient client(espClient);
DynamicJsonDocument doc(16384);
char test_buffer[16384];

Adafruit_MLX90640 mlx;
float frame[32 * 24]; // buffer for full frame of temperatures
//int buffer_thermal[768];
char buf[2000];

//low range of the sensor (this will be blue on the screen)
//int MINTEMP = minTempThresh;

//high range of the sensor (this will be red on the screen)
//int MAXTEMP = maxTempThresh;

uint16_t displayPixelWidth, displayPixelHeight;

void startup_message() {
  const char* startupPayload = "{\"type\": \"startup\", \"device_id\": 1, \"description\": \"launching\", \"battery\": 80}";
  client.beginPublish("/plant", strlen(startupPayload), false);
  for (int i = 0; i < strlen(startupPayload); i ++) {
    client.write((uint8_t)startupPayload[i]);
  }
//  client.write(willPayload, strlen(willPayload));
  Serial.println("END_PUB for startup");
  client.endPublish();
}

void setup() {
  Serial.begin(9600);
  pinMode(33, INPUT); // 12, 21, 14
  pinMode(12, INPUT);
  pinMode(21, INPUT);
  pinMode(27, INPUT);
  pinMode(lightON, OUTPUT);
  ledcSetup(0, 1E5, 12);
  ledcAttachPin(15, 0);
//  WiFi.begin(ssid, passphrase);
  WiFi.begin(ssid);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
    Serial.println(ssid);
  }

  Serial.println("Connected to WiFi.");
  client.setKeepAlive(60);
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");
    if (client.connect("ESP32Client", mqttUser, mqttPassword, "/plant", willQos, willRetain, willPayload )) {
      Serial.println("MQTT connected");
      client.subscribe("/plant", 1);
      startup_message();
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

  //play tone
  tone(15, melody[4]);
  delay(1000);
  tone(15, END);
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  if (DEBUG_LEVEL >= 1) {
    Serial.print(". Message: ");
  }
  String messageTemp;

  for (int i = 0; i < length; i++) {
    if (DEBUG_LEVEL >= 1) {
      Serial.print((char)message[i]);
    }
    messageTemp += (char)message[i];
  }
  Serial.println();

  // Feel free to add more if statements to control more GPIOs with MQTT

  if (String(topic) == "/plant") {
    Serial.print("...Parsing JSON...: ");
    messageTemp.toCharArray(buf, 1000);
    Serial.println("written to byte array");
    parseJson();
  }
}

void attachMeta(int message_type) {
  int battery = 55;  // TODO: MEASURE THIS

  doc[MESSAGE_KEY_DEVICE] = device_id;
  doc[MESSAGE_KEY_BATTERY] = battery;
  doc[MESSAGE_KEY_DESCRIPTION] = "hello hello!";
  
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

void parseJson() {
  DynamicJsonDocument tempdoc(1024);
  tempdoc.clear();
  deserializeJson(tempdoc, buf);

  const char* message_type = tempdoc[MESSAGE_KEY_TYPE];
  int in_device_id = tempdoc[MESSAGE_KEY_DEVICE];

  String in_message_type, compare_message_type1, compare_message_type2;
  in_message_type = String(message_type);
  Serial.println(in_message_type);
  compare_message_type1 = String(MESSAGE_TYPE_POWER_ON);
  compare_message_type2 = String(MESSAGE_TYPE_POWER_OFF);

  if (in_device_id == device_id) {
    if (in_message_type == compare_message_type1) {
      Serial.println("TURN ON REMOTE");
      remote_on = true;
    } else if (in_message_type == compare_message_type2) {
      Serial.println("TURN OFF REMOTE");
      remote_on = false;
    }
    if (in_message_type == compare_message_type1 || in_message_type == compare_message_type2) {
      minTempThresh = tempdoc[MESSAGE_KEY_MINTEMP];
      maxTempThresh = tempdoc[MESSAGE_KEY_MAXTEMP];
      countThresh = tempdoc[MESSAGE_KEY_COUNT];
      colorIndexThresh = tempdoc[MESSAGE_KEY_COLORINDEX];
    
      Serial.print("minTemp..."); Serial.println(minTempThresh);
      Serial.print("maxTemp..."); Serial.println(maxTempThresh);
      Serial.print("count..."); Serial.println(countThresh);
      Serial.print("colorIndex..."); Serial.println(colorIndexThresh);
    }
  }
}

void deter() {
  int melodyLength = sizeof(melody) / sizeof(int);
  for (int count = 0; count < 10; count++) {
    for (int thisNote = 0; thisNote < melodyLength; thisNote++) {
      if (DEBUG_LEVEL >= 2) {
        Serial.println(thisNote);
      }
      if (SOUND_ENABLED) {
        tone(15, melody[thisNote]);
      }
      if (blink == 0) {
        state = !state;
        digitalWrite(lightON, state);
      }
      blink++;
      if (blink == 7) {
        blink = 0;
      }
      delay(30);
    }
  }
  delay(30);
  digitalWrite(lightON, LOW);
}

void readImageAndSendMessage() {
  // json pre metadata
  doc.clear();
  attachMeta(1);
  int count = 0;
  int sqCount = 0;
  for (uint8_t h = 0; h < 24; h++) {
    char row_index[20];
    sprintf(row_index, "camValue%u", h);
    doc[row_index];
    for (uint8_t w = 0; w < 32; w++) {
      float t = frame[h * 32 + w];

      if (t > maxTempThresh) {
        t = maxTempThresh;
      }
      else if (t < minTempThresh) {
        t = minTempThresh;
      }

      if (t > 15) {
        sqCount = sqCount + 1;
      }
      uint8_t colorIndex = map(t, minTempThresh, maxTempThresh, 0, 255);

      colorIndex = constrain(colorIndex, 0, 255);

      if (colorIndex > colorIndexThresh) {
        count = count + 1;
      }

      doc[row_index][w] = colorIndex;
    }
  }

  Serial.println(count);
  Serial.print("...");
  Serial.println(sqCount);
  if (count > countThresh && count < 600) { //6.5% of entire image is "warm"
    Serial.println("PEST DETECTED");
    size_t n = serializeJson(doc, test_buffer);
    client.beginPublish("/plant", n, false);
    for (int i = 0; i < n; i++) {
      client.write(test_buffer[i]);
    }
    Serial.println("END_PUB");
    client.endPublish();
    deter();
  }
  else {
    Serial.println("NO PEST");
  }
}

void send_blink() {
  const char* startupPayload = "{\"type\": \"startup\", \"device_id\": 1, \"description\": \"pinging\", \"battery\": 79}";
  client.beginPublish("/plant", strlen(startupPayload), false);
  for (int i = 0; i < strlen(startupPayload); i ++) {
    client.write((uint8_t)startupPayload[i]);
  }
  Serial.println("END_PUB for startup");
  client.endPublish();
}

void loop() {
  // reconnect behavior
  int status = WiFi.status();
  if (DEBUG_LEVEL >= 2) {
    Serial.print("Wifi status: ");
    Serial.println(status); // 3 is good
  }
  if (status != WL_CONNECTED) {
    Serial.print("Attempting to reconnect to WiFi network");
    status = WiFi.begin(ssid);
//    status = WiFi.begin(ssid, passphrase);
    if (status != WL_CONNECTED) {
      Serial.println("Connection failed, continuing loop");
    }
  }

  if (!client.connected()) {
    client.setKeepAlive(60);
    client.setServer(mqttServer, mqttPort);
    client.setCallback(callback);
    Serial.println("Connecting to MQTT...");
    if (client.connect("ESP32Client", mqttUser, mqttPassword, "/plant", willQos, willRetain, willPayload )) {
      Serial.println("MQTT connected");
      client.subscribe("/plant", 1);
      startup_message();
    } else {
      Serial.print("failed with state ");
      Serial.print(client.state());
      delay(2000);
    }
  } else {
    if (DEBUG_LEVEL >= 2) {
      Serial.println("Still connected to MQTT...");
    }
    client.loop();
  }

  // main loop!!!
//  client.loop(); // TODO: TYLER IF TIMEOUT FAILS, THIS NEEDS TO BE RELOCATED
  if (remote_on) { // TODO: ADD MORE BOOLEANS AND LOGIC FOR ON STATUS remote_on
    if (digitalRead(33) == HIGH || digitalRead(12) == HIGH || digitalRead(21) == HIGH || digitalRead(27) == HIGH) {
      Serial.println("PIR Triggered");
      uint32_t timestamp = millis();
      if (mlx.getFrame(frame) != 0) {
        Serial.println("Failed thermal");
        delay(1000);
        return;
      }
      //    int colorTemp;
      readImageAndSendMessage();

      counter++;
      Serial.print((millis() - timestamp) / 2); Serial.println(" ms per frame (2 frames per display)");
      Serial.print(2000.0 / (millis() - timestamp)); Serial.println(" FPS (2 frames per display)");
      //
      delay(100);
    }
  } else {
    Serial.println("Remote off, skipping");
    delay(1000);
  }
  if((millis() - previousTime) > 30 * 1000) {
    previousTime = millis();   
    send_blink();
  }
}