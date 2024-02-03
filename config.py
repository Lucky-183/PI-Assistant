import json
from datetime import datetime

# 控制变量,不可为None
parmas = {
    # 线程锁 LOCK
    "notify_enable": False,
    "chat_enable": False,
    "rec_enable": False,  # wifi module
    # 参量
    "command": "",
    "music_volume": 0.25,
    "general_volume": 0.5,
    "wakebyhw": False,
    "hw_started": False,
    "Noticenotify": True,
    "timenotify": True,
    "MusicPlay": False,
    # 外设
    "dev_demo": False,
    # ... 可以添加更多的参数
}
# 这里列出需要追踪的参数
tracked_params = [
    "music_volume",
    "general_volume",
    "wakebyhw",
    "Noticenotify",
    "timenotify",
    "MusicPlay",
    "dev_demo"
]
# WebUI可修改的参数
allow_params = [
    "command",
    "music_volume",
    "general_volume",
    "wakebyhw",
    "Noticenotify",
    "timenotify",
    "MusicPlay",
]


class ConfigManager:
    def __init__(self, params, tracked_params, allow_params):
        self.params = params
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
            else:
                raise ValueError(f"Unknown status key: {key}")
        if changed_params:
            self.write_to_file(changed_params)
            # 打印所有改变的参数
            print(changed_params)

    def get(self, key):
        """获取参数的值"""
        return self.params.get(key, None)


# 创建单例
config = ConfigManager(parmas, tracked_params, allow_params)
