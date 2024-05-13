from config import config
import requests
import time
#HASS的REST API
url_check_config = "http://127.0.0.1:8123/api/config"
url_check_service= "http://127.0.0.1:8123/api/services"
url_demo_service_light_on = "http://127.0.0.1:8123/api/services/light/turn_on"
url_demo_service_light_off = "http://127.0.0.1:8123/api/services/light/turn_off"

headers = {
    "Authorization": "Bearer xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "content-type": "application/json",
}
data = {"entity_id": "light.yeelink_lampxx_xxxx_light"}
# response=requests.get(url_check_config,headers=headers)
# response=requests.get(url_check_service,headers=headers)

def handle():
    status = config.get("HA_light_demo")
    while(1):
        if status != config.get("HA_light_demo"):
            status = config.get("HA_light_demo")
            if status :
                response=requests.post(url_demo_service_light_on, headers=headers, json=data)
                print('light on')
            else:
                response=requests.post(url_demo_service_light_off, headers=headers, json=data)
                print('light off')
        time.sleep(2)