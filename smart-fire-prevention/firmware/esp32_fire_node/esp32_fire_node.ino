/*
 * Smart Fire Prevention & Suppression - ESP32 Sensor/Actuator Node
 * Sensors : DHT22 (temp/humidity), MQ-2 (smoke/gas), flame sensor (digital)
 * Actuators: buzzer, relay (water pump / suppression valve)
 * Comms   : MQTT over WiFi
 * Libraries: PubSubClient, DHT sensor library, ArduinoJson
 */
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ---------- CONFIG ----------
const char* WIFI_SSID   = "YOUR_WIFI_SSID";
const char* WIFI_PASS   = "YOUR_WIFI_PASSWORD";
const char* MQTT_BROKER = "192.168.1.100";   // IP of your MQTT broker
const int   MQTT_PORT   = 1883;
const char* NODE_ID     = "node1";

#define DHT_PIN     4
#define DHT_TYPE    DHT22
#define MQ2_PIN     34      // analog input
#define FLAME_PIN   27      // LOW = flame detected (most modules)
#define BUZZER_PIN  26
#define RELAY_PIN   25      // HIGH = pump ON (change if relay is active-low)

const float TEMP_FAILSAFE_C = 60.0;  // local fail-safe threshold
const int   GAS_FAILSAFE    = 2500;  // raw ADC (0-4095)
const unsigned long PUBLISH_MS = 2000;

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient espClient;
PubSubClient mqtt(espClient);

String topicSensors, topicCmd;
bool pumpOn = false;
unsigned long lastPublish = 0;

void setPump(bool on) {
  pumpOn = on;
  digitalWrite(RELAY_PIN, on ? HIGH : LOW);
  digitalWrite(BUZZER_PIN, on ? HIGH : LOW);
}

void onMessage(char* topic, byte* payload, unsigned int len) {
  String msg;
  for (unsigned int i = 0; i < len; i++) msg += (char)payload[i];
  msg.trim();
  if (msg == "PUMP_ON")  setPump(true);
  if (msg == "PUMP_OFF") setPump(false);
  if (msg == "ALERT")    digitalWrite(BUZZER_PIN, HIGH);
  if (msg == "CLEAR")    digitalWrite(BUZZER_PIN, LOW);
}

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWiFi connected: " + WiFi.localIP().toString());
}

void connectMQTT() {
  while (!mqtt.connected()) {
    if (mqtt.connect(NODE_ID)) {
      mqtt.subscribe(topicCmd.c_str());
      Serial.println("MQTT connected");
    } else {
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(FLAME_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);
  setPump(false);
  dht.begin();

  topicSensors = String("fire/") + NODE_ID + "/sensors";
  topicCmd     = String("fire/") + NODE_ID + "/cmd";

  connectWiFi();
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setCallback(onMessage);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();
  if (!mqtt.connected()) connectMQTT();
  mqtt.loop();

  if (millis() - lastPublish >= PUBLISH_MS) {
    lastPublish = millis();

    float t = dht.readTemperature();
    float h = dht.readHumidity();
    int gas = analogRead(MQ2_PIN);
    bool flame = (digitalRead(FLAME_PIN) == LOW);
    if (isnan(t)) t = -1;
    if (isnan(h)) h = -1;

    // Local fail-safe: act even if WiFi/server/AI is down
    if (flame && (t > TEMP_FAILSAFE_C || gas > GAS_FAILSAFE)) setPump(true);

    StaticJsonDocument<200> doc;
    doc["node"] = NODE_ID;
    doc["temp"] = t;
    doc["hum"] = h;
    doc["gas"] = gas;
    doc["flame"] = flame;
    doc["pump"] = pumpOn;
    char buf[200];
    serializeJson(doc, buf);
    mqtt.publish(topicSensors.c_str(), buf);
    Serial.println(buf);
  }
}
