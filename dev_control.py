import threading
import time
import paho.mqtt.client as mqtt
from config import config
from Scene import status_manager
from threading import Event
MQTT_BROKER = '127.0.0.1'
MQTT_PORT = 1883

#定义设备,设定订阅主题与发布主题
devices={
    "sensor_demo":{
        "type":"input",
        "sub_topic": ["sensor_demo/value"],
        "pub_topic": "sensor_demo/ack"
    },
    "dev_demo":{
        "type":"output",
        "pub_topic": "dev_demo/value",
        "sub_topic": ["dev_demo/ack"]
    }
}

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(client_id="MasterClient")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.dev_status = {dev: config.get(dev) for dev in devices}  # 设备字典，初始状态为None
        self.dev_ack_received = {dev: Event() for dev in devices}

        # 启动一个线程来处理MQTT网络通信
        threading.Thread(target=self.client.loop_start, daemon=True).start()

        # 启动状态监测线程
        threading.Thread(target=self.monitor_dev_status, daemon=True).start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        for dev in devices.values():
            for topic in dev['sub_topic']:
                client.subscribe(topic)

    def on_message(self, client, userdata, msg):

        print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
        #通过msg获取设备名称和消息
        for dev, topics in devices.items():
            if msg.topic in topics['sub_topic']:
                #如果以ack结尾
                if msg.topic.endswith('ack'):
                    self.dev_ack_received[dev].set()
                    print(f"Ack received from {dev}.")
                else:
                    sensor_value = msg.payload.decode() == 'True'
                    status_manager.set_status(dev, sensor_value)
                    client.publish(topics['pub_topic'], "ACK:"+str(sensor_value))
                    print(f"Published ACK:{sensor_value} to {topics['pub_topic']}")
                break
    
    def monitor_dev_status(self):
        while True:
            for dev, topics in devices.items():
                if topics['type'] == 'output':
                    current_status = config.get(dev)  # 假设config是一个全局的配置状态管理器
                    if current_status != self.dev_status[dev]:
                        # 发布新状态
                        self.client.publish(topics['pub_topic'], str(current_status))
                        print(f"Published {current_status} to {topics['pub_topic']}")
                        # 等待设备响应或超时（假设5秒超时）
                        if not self.dev_ack_received[dev].wait(5):
                            print(f"No ack received from {dev}, resetting status.")
                            # 如果没有收到ack，复位设备状态
                            config.set(**{dev: self.dev_status[dev]})  # 假设config有一个set方法来更新设备状态
                            print(f"Reset status of {dev} to {self.dev_status[dev]}")
                        else:
                            # 如果收到ack，更新最后的设备状态，并清除事件标志以便下一次使用
                            self.dev_status[dev] = current_status
                            self.dev_ack_received[dev].clear()
            time.sleep(1)  # 延迟1秒再次检查状态，避免过于频繁的检查    

if __name__ == "__main__":
    client = MQTTClient()
