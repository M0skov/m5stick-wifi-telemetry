//Jan Israel Charrez Gomez
//Lab 3 - WiFi telemetry over MQTT
//Instructor Kyle Jonhsen
#include "M5Unified.h"
#include "wifi_final_version.h"
#include "PubSubClient.h"
#include <Preferences.h>

Preferences preferences;
M5Canvas canvas(&M5.Display);
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
char username[50];
char password[50];
char ssid[50];

const char *MOVEMENT_TOPIC ="elee2045/jan_gomez_FINAL/movement";
const char *BATTERY_TOPIC = "elee2045sp25/jan_gomez_FINAL/battery";
const char *SOUND_TOPIC ="elee2045/jan_gomez_FINAL/sound";
const char *RATE_TOPIC = "elee2045sp25/jan_gomez_FINAL/rate";
const char *VELOCITY_TOPIC ="elee2045/jan_gomez_FINAL/velocity";

uint32_t DURATION_OF_DATA = 3000;
unsigned long last_attempt_time = 0;
float vx = 0;
float vy = 0;
float vz = 0;
#define NUM_SAMPLES 400
int16_t samples[NUM_SAMPLES];

float getAverageMicVolume() {
  for (int i = 0; i < 5; i++) {
    M5.Mic.record(samples, NUM_SAMPLES);
  }
  int32_t avg = 0;
  for (int i = 0; i < NUM_SAMPLES; i++) avg += abs(samples[i]);
  avg /= NUM_SAMPLES;
  return avg / (float)(0x7FFF);
}

void mqttMessageCallback(char *topic, uint8_t* payload, unsigned int length) {
  if (strcmp(topic, RATE_TOPIC) == 0 && length == sizeof(uint32_t)) {
    memcpy(&DURATION_OF_DATA, payload, length);
    preferences.putULong("interval", DURATION_OF_DATA);
    canvas.clear();
    canvas.setCursor(10, 10);
    canvas.printf("Got Rate: %lu ms", DURATION_OF_DATA);
    canvas.pushSprite(0, 0);
  }
}

void connectToMQTT() {
  canvas.clear();
  canvas.setCursor(10, 10);
  canvas.println("Connectin MQTT");
  if (!mqttClient.connect("", "giiuser", "giipassword")) {
    canvas.setCursor(10, 30);
    canvas.printf("MQTT failed, rc=%d", mqttClient.state());
  } else {
    canvas.setCursor(10, 30);
    canvas.println("MQTT connected");
    mqttClient.subscribe(RATE_TOPIC);
  }
  canvas.pushSprite(0, 0);
}

void setup() {
  M5.begin();
  M5.Mic.begin();
  Serial.begin(115200);
  M5.Display.setRotation(1);
  canvas.createSprite(M5.Display.width(), M5.Display.height());

  mqttClient.setServer("eduoracle.ugavel.com", 1883);
  mqttClient.setCallback(mqttMessageCallback);

  preferences.begin("wifi", false);
  preferences.getString("ssid", ssid, 50);
  preferences.getString("username", username, 50);
  preferences.getString("password", password, 50);
  DURATION_OF_DATA = preferences.getULong("interval", 5000);
}

void loop() {
  while (WiFi.status() != WL_CONNECTED || !mqttClient.connected()) {
    connectToWifi(ssid, username, password);
    connectToMQTT();
  }
  float ax = 0.0;
  float ay = 0.0;
  float az = 0.0;
  float gx = 0.0;
  float gy = 0.0;
  float gz = 0.0;

  M5.Imu.getAccel(&ax, &ay, &az);
  M5.Imu.getGyro(&gx, &gy, &gz);

  float timet = DURATION_OF_DATA / 1000.0;
  vx = vx + ax * timet;
  vy = vy + ay * timet;
  vz = vz + az * timet;

  float movement_data[6] = {ax, ay, az, gx, gy, gz};
  float velocity_data[3] = {vx, vy, vz};
  int16_t battery = M5.Power.getBatteryVoltage();
  float sound_level = getAverageMicVolume();

  mqttClient.publish(MOVEMENT_TOPIC, (uint8_t*)movement_data, sizeof(movement_data));
  mqttClient.publish(VELOCITY_TOPIC, (uint8_t*)velocity_data, sizeof(velocity_data));
  mqttClient.publish(BATTERY_TOPIC, (uint8_t*)&battery, sizeof(int16_t));
  mqttClient.publish(SOUND_TOPIC, (uint8_t*)&sound_level, sizeof(float));

  if (DURATION_OF_DATA < 15000) {
    while (millis() - last_attempt_time < DURATION_OF_DATA) {
      M5.delay(1);
      mqttClient.loop();
    }
    mqttClient.loop();
    last_attempt_time = millis();
    return;
  }
}
