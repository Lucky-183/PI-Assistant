from config import config
from play import play

# 状态量,可为None
device_state = {
    "music_playing": False,
    "time": None,
    "user_status": "offline",
    "sensor_demo": None,
    "HA_light_demo": None
}
# 场景条件（越靠前优先级越高）
condition = {
    "demo1": {"sensor_demo": True},
    "demo2": {"sensor_demo": False},
    "Morning": {"time": (6, 9, 0, 0), "user_status": None},
    "Night": {"time": (23, 5, 0, 0), "user_status": None},
}


# 执行动作
def deal_condition(scene):
    if scene == "Morning":
        config.set(
            Noticenotify=True, timenotify=True, general_volume=0.8, music_volume=0.3
        )
        play("Sound/goodmorning.raw")
    elif scene == "Night":
        play("Sound/goodnight.raw")
        config.set(
            Noticenotify=False, timenotify=False, general_volume=0.5, music_volume=0.1
        )
    elif scene == "demo1":
        config.set(dev_demo=True)
    elif scene == "demo2":
        config.set(dev_demo=False)
