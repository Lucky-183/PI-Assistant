import threading
import time
import paho.mqtt.client as mqtt
from config import config
from Scene import status_manager
from threading import Event
from loguru import logger
MQTT_BROKER = '127.0.0.1'
MQTT_PORT = 1883
USERNAME = 'pi'
PASSWORD = '123456'
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
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.dev_status = {dev: config.get(dev) for dev in devices}  # 设备字典，初始状态为None
            self.dev_ack_received = {dev: Event() for dev in devices}

            # 启动一个线程来处理MQTT网络通信
            threading.Thread(target=self.client.loop_start, daemon=True).start()

            # 启动状态监测线程
            threading.Thread(target=self.monitor_dev_status, daemon=True).start()
        except Exception as e:
            logger.error(f"Could not connect to MQTT server: {e}")

    def on_connect(self, client, userdata, flags, rc):
        logger.info("MQTT Client：Connected with result code "+str(rc))
        for dev in devices.values():
            for topic in dev['sub_topic']:
                client.subscribe(topic)

    def on_message(self, client, userdata, msg):

        logger.info(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
        #通过msg获取设备名称和消息
        for dev, topics in devices.items():
            if msg.topic in topics['sub_topic']:
                #如果以ack结尾，表示是输出设备
                if msg.topic.endswith('ack'):
                    # 如果收到的消息是同步消息，更新设备状态
                    if msg.payload.decode().startswith('sync'):
                        sync_value = msg.payload.decode().split(":")[1]
                        if sync_value == "True" or sync_value == "False":
                            sync_value = sync_value == "True"
                        config.set(**{dev: sync_value})
                        logger.info(f"synced status of {dev} to {msg.payload.decode().split(':')[1]}")
                    else:
                        self.dev_ack_received[dev].set()
                        logger.info(f"Ack received from {dev}.")
                #否则是输入设备
                else:
                    sensor_value = msg.payload.decode()
                    status_manager.set_status(**{dev:sensor_value}) #输入设备的状态设定
                    client.publish(topics['pub_topic'], "ACK:"+str(sensor_value))
                    logger.info(f"Published ACK:{sensor_value} to {topics['pub_topic']}")
                break
    
    def monitor_dev_status(self):
        while True:
            for dev, topics in devices.items():
                if topics['type'] == 'output':
                    current_status = config.get(dev)  # config是一个全局的配置状态管理器
                    if current_status != self.dev_status[dev]:
                        # 发布新状态
                        self.client.publish(topics['pub_topic'], str(current_status), retain=True)
                        logger.info(f"Published {current_status} to {topics['pub_topic']}")
                        # 等待设备响应或超时（假设5秒超时）
                        if not self.dev_ack_received[dev].wait(5):
                            logger.warning(f"No ack received from {dev}, resetting status.")
                            # 如果没有收到ack，复位设备状态
                            config.set(**{dev: self.dev_status[dev]})  # config有一个set方法来更新设备状态
                            logger.warning(f"Reset status of {dev} to {self.dev_status[dev]}")
                        else:
                            # 如果收到ack，更新最后的设备状态，并清除事件标志以便下一次使用
                            self.dev_status[dev] = current_status
                            self.dev_ack_received[dev].clear()
            time.sleep(1)  # 延迟1秒再次检查状态，避免过于频繁的检查    


client = MQTTClient()
