import threading
from datetime import datetime
from config import config
from play import play
class StatusManager:
    def __init__(self, callback=None):
        # 初始化状态集
        self.states = {
            "music_playing": False,
            "current_time": datetime.now(),
            "user_status": "offline"
            # 更多状态可以在这里添加
        }
        self.callback = callback  # 当状态改变时的回调函数
        self._start_time_updater()

    def _start_time_updater(self):
        """启动一个定时任务，每分钟更新一次时间状态"""
        self._update_time()
        threading.Timer(30, self._start_time_updater).start()

    def _update_time(self):
        """更新时间状态并触发回调"""
        self.states["current_time"] = datetime.now()
        if self.callback:
            self.callback(self.states)

    def set_status(self, key, value):
        """设置状态的值，并触发回调"""
        if key in self.states:
            self.states[key] = value
            if self.callback:
                self.callback(self.states)
        else:
            raise ValueError(f"Unknown status key: {key}")

    def get_status(self, key):
        """获取状态的值"""
        return self.states.get(key, None)

    def __str__(self):
        return str(self.states)


class SceneManager:
    current_scene = "Unknown Scene"  # 类变量，跟踪当前活动的场景

    @staticmethod
    def check_scenes(states):
        """根据状态检查并返回匹配的场景"""
        new_scene = "Unknown Scene"
        
        if SceneManager.is_morning(states):
            new_scene = "Morning"
        elif SceneManager.is_night(states):
            new_scene = "Night"
        elif SceneManager.is_returning_home(states):
            new_scene = "Returning Home"
        elif SceneManager.is_leaving_home(states):
            new_scene = "Leaving Home"

        if new_scene != SceneManager.current_scene:
            SceneManager.current_scene = new_scene  # 更新当前活动的场景
            return new_scene  # 返回新场景
        else:
            return None  # 没有场景更改

    @staticmethod
    def is_morning(states):
        """判断是否是早晨"""
        current_hour = states["current_time"].hour
        return 8 <= current_hour < 23

    @staticmethod
    def is_night(states):
        """判断是否是晚上"""
        current_hour = states["current_time"].hour
        return  0 <= current_hour < 8

    @staticmethod
    def is_returning_home(states):
        """判断用户是否正在回家"""
        return states["user_status"] == "online"

    @staticmethod
    def is_leaving_home(states):
        """判断用户是否正在离家"""
        return states["user_status"] == "offline"


def on_status_change(states):
    """当状态改变时的回调函数"""
    scene = SceneManager.check_scenes(states)
    if scene:  # 如果场景改变了
        if scene == "Morning":
            
            config.set(Noticenotify=True, timenotify=True, general_volume=0.8, music_volume=0.3)
            play('Sound/goodmorning.raw')
        elif scene == "Night":
            play('Sound/goodnight.raw')
            config.set(Noticenotify=False, timenotify=False, general_volume=0.5, music_volume=0.1)
        print(f"Current scene: {scene}")
        
        with open("Log/scene_changes.txt", "a") as f:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{current_time} - Scene changed to: {scene}\n")

        print(f"Current scene: {scene}")
    else:
        pass


# 使用方法
status_manager = StatusManager(callback=on_status_change)

