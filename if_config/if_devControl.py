from config import config
from play import play

def detect(text):
    if text == "开灯。":
        config.set(dev_demo=True)
        return True
    elif text == "关灯。":
        config.set(dev_demo=False)
        return True
    elif text == "打开台灯。":
        config.set(HA_light_demo=True)
        return True
    elif text == "关闭台灯。":
        config.set(HA_light_demo=False)
        return True
    return False

