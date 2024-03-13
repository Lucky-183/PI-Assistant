#include <WiFi.h>
#include <PubSubClient.h>

// WiFi设置
const char* ssid = "****************";
const char* password = "******************";

// MQTT服务器设置
const char* mqtt_server = "192.168.1.30"; // MQTT Broker的IP地址
const int mqtt_port = 1883;
const char* mqtt_user = "pi"; // 如果有的话
const char* mqtt_password = "123456"; // 如果有的话
const int ledPin = 2;
// MQTT 主题
const char* value_topic = "dev_demo/value";
const char* ack_topic = "dev_demo/ack";

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  if(message == "True") {
    digitalWrite(ledPin, HIGH); // 打开LED
    Serial.println("LED turned ON");
  } else if(message == "False") {
    digitalWrite(ledPin, LOW); // 关闭LED
    Serial.println("LED turned OFF");
  }
  
  // 发送确认消息
  client.publish(ack_topic, "OK");
  
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // 尝试连接
    if (client.connect("ESP32Client", mqtt_user, mqtt_password)) {
      Serial.println("connected");
      // 订阅
      client.subscribe(value_topic);
          } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // 等待5秒后重试
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  pinMode(ledPin, OUTPUT);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
