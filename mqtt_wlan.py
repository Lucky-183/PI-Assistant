import paho.mqtt.client as mqtt
from dev_control import devices
from Scene import status_manager
from config import config
import threading
from loguru import logger
host = "183.230.40.39" #中国移动MQTT地址
port = 6002 #端口
client_id = "12033****" #设备ID
product_id = "62****" #产品ID以及鉴权信息
password = "******"


class MQTTWlanClient:

    def __init__(self):
        self.client = mqtt.Client(client_id)
        self.client.username_pw_set(product_id, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(host, port)

        # 启动一个线程来处理MQTT网络通信
            threading.Thread(target=self.client.loop_start, daemon=True).start()
        except Exception as e:
            logger.warning(f"Could not connect to MQTT server: {e}")

    def on_connect(self, client, userdata, flags, rc):
        logger.info("Wlan MQTT：Connected with result code " + str(rc))
        client.subscribe("input")
        client.subscribe("output")
        client.subscribe("message_pi")


    def on_message(self, client, userdata, msg):
        logger.info("WLAN_MQTT received :" + msg.topic + " " + msg.payload.decode("utf-8"))
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        if topic == "input":
            if payload:
                if payload.split(':')[0] in devices.keys() and devices[payload.split(':')[0]]["type"] == "input":
                    sensor_name = payload.split(':')[0]
                    sensor_value = payload.split(':')[1]
                    logger.info(f"From input device: {sensor_name} value: {sensor_value}")
                    client.publish("message_ack", f"Received {sensor_name} value: {sensor_value}")
                    status_manager.set_status(**{sensor_name:sensor_value})


        if topic == "output":
            if payload:
                if payload.split(':')[0] in devices.keys() and devices[payload.split(':')[0]]["type"] == "output":
                    dev_name = payload.split(':')[0]
                    dev_value = payload.split(':')[1]
                    if dev_value == "True" or dev_value == "False":
                        dev_value = dev_value == "True"
                    logger.info(f"From output device:  {dev_name}  value:  {dev_value}")
                    client.publish("message_ack", f"Received {dev_name} value: {dev_value}")
                    config.set(**{dev_name:dev_value})
                    

        if topic == "message_pi":
            if payload and config.get("mqtt_message") is False:
                config.set(command=payload)
                config.set(mqtt_message=True)
                logger.debug(f"Command received: {payload}")

    def send_message(self, message):
        self.client.publish("message_endpoint", message)


wlan_client=MQTTWlanClient()
