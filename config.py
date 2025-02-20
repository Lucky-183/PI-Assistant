import json
from datetime import datetime
from loguru import logger

# 控制变量,不可为None
parmas = {
    # 线程锁 LOCK
    "notify_enable": False,
    "chat_enable": False,
    "rec_enable": False,  # wifi module
    "mqtt_message": False,
    # 参量
    "command": "",
    "answer": "晓晓已上线，有什么可以帮您的吗？",
    "music_volume": 0.25,
    "general_volume": 0.5,
    "wakebyhw": False,
    "hw_started": False,
    "Noticenotify": True,
    "timenotify": True,
    "MusicPlay": False,
    # ... 可以添加更多的参数
}
# 外设控制参数
device_params = {
    "dev_demo": False,
    "HA_light_demo": False, # HASS外设
}

param_types = {
    # "command": "string",
    # "music_volume": "float",
    "dev_demo": "bool",
    "HA_light_demo": "bool"
}

# 这里列出需要追踪的参数
tracked_params = [
    "music_volume",
    "general_volume",
    "wakebyhw",
    "Noticenotify",
    "timenotify",
    "MusicPlay",
    "dev_demo",
    "HA_light_demo",
]
# WebUI可修改的参数
allow_params = [
    "answer",
    "command",
    "music_volume",
    "general_volume",
    "wakebyhw",
    "Noticenotify",
    "timenotify",
    "MusicPlay",
]


class ConfigManager:
    def __init__(self, params, device_params, tracked_params, allow_params):
        self.params = params
        self.device_params = device_params
        self.tracked_params = tracked_params
        self.allow_params = allow_params

    def write_to_file(self, changed_params):
        """将当前的参数状态写入到文件"""
        with open("Log/config_state.txt", "a") as file:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_data = {
                "timestamp": current_time,
                "changed_params": changed_params,  # 只记录发生变化的参数
            }
            file.write(json.dumps(formatted_data, indent=4) + "\n\n")

    def set(self, **kwargs):
        """设置参数的值"""
        changed_params = {}  # 记录发生变化的参数
        for key, value in kwargs.items():
            if key in self.params:
                # 如果该参数在追踪列表中且值发生了变化，则记录
                if (key in self.tracked_params) and self.params[key] != value:
                    changed_params[key] = value
                # 更新参数值
                self.params[key] = value
            elif key in self.device_params:
                # 追踪外设参数变更
                if key in self.tracked_params and self.device_params[key] != value:
                    changed_params[key] = value
                self.device_params[key] = value
            else:
                logger.warning(f"Unknown config key: {key}")
        if changed_params:
            self.write_to_file(changed_params)
            # 打印所有改变的参数
            logger.info(f'Changed_params:{changed_params}')

    def get(self, key):
        """获取参数的值"""
        return self.params.get(key) if key in self.params else self.device_params.get(key, None)


# 创建单例
config = ConfigManager(parmas, device_params, tracked_params, allow_params)
