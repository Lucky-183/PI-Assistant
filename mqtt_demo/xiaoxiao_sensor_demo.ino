#include <WiFi.h>
#include <PubSubClient.h>

// WiFi和MQTT服务器配置
const char* ssid = "********";
const char* password = "**********";
const char* mqtt_server = "192.168.1.30"; // MQTT Broker的IP地址
const int mqttPort = 1883;
const char* mqtt_user = "pi"; // 如果有的话
const char* mqtt_password = "123456"; // 如果有的话

WiFiClient espClient;
PubSubClient client(espClient);

bool sensorValue = false; // 初始值为false

void setupWifi() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi connected");
  Serial.println("IP address: " + WiFi.localIP().toString());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // 尝试连接
    if (client.connect("ESP32SensorDemo", mqtt_user, mqtt_password)) {
      Serial.println("connected");
      client.subscribe("sensor_demo/ack");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  setupWifi();
  client.setServer(mqtt_server, mqttPort);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // 交替发送"True"和"False"
  sensorValue = !sensorValue;
  String message = sensorValue ? "True" : "False";
  Serial.print("Publishing sensor value: ");
  Serial.println(message);
  client.publish("sensor_demo/value", message.c_str());

  delay(5000); // 等待10秒后再次发送
}
