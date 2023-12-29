import threading
from datetime import datetime
from config import config
from play import play

class StatusManager:
    def __init__(self, callback=None):
        self.states = {
            "music_playing": False,
            "current_time": datetime.now(),
            "user_status": "offline"
        }
        self.callback = callback
        self._start_time_updater()

    def _start_time_updater(self):
        self._update_time()
        threading.Timer(30, self._start_time_updater).start()

    def _update_time(self):
        self.states["current_time"] = datetime.now()
        if self.callback:
            self.callback(self.states)

    def set_status(self, key, value):
        if key in self.states:
            self.states[key] = value
            if self.callback:
                self.callback(self.states)
        else:
            raise ValueError(f"Unknown status key: {key}")

    def get_status(self, key):
        return self.states.get(key, None)

    def __str__(self):
        return str(self.states)


class SceneManager:
    current_scene = "Unknown Scene"
    scene_conditions = {
        "Morning": {"time_range": (8, 23), "user_status": "online"},
        "Night": {"time_range": (0, 8), "user_status": None},
    }

    @staticmethod
    def check_scenes(states):
        for scene, conditions in SceneManager.scene_conditions.items():
            if SceneManager._scene_match(states, conditions):
                if scene != SceneManager.current_scene:
                    SceneManager.current_scene = scene
                    return scene
        # 如果没有匹配的场景，设置为 'Unknown Scene'
        if SceneManager.current_scene != "Unknown Scene":
            SceneManager.current_scene = "Unknown Scene"
            return "Unknown Scene"

        return None

    @staticmethod
    def _scene_match(states, conditions):
        for key, value in conditions.items():
            if key == "time_range":
                if not (value[0] <= states["current_time"].hour < value[1]):
                    return False
            elif value is not None and states.get(key) != value:
                return False
        return True


def on_status_change(states):
    scene = SceneManager.check_scenes(states)
    if scene:
        if scene == "Morning":
            config.set(notify=True, time_notify=True, general_volume=0.8, music_volume=0.3)
            play('Sound/goodmorning.raw')
        elif scene == "Night":
            play('Sound/goodnight.raw')
            config.set(notify=False, time_notify=False, general_volume=0.5, music_volume=0.1)
        
        with open("Log/scene_changes.txt", "a") as f:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{current_time} - Scene changed to: {scene}\n")

        print(f"Current scene: {scene}")
    else:
        pass

# 使用方法
status_manager = StatusManager(callback=on_status_change)


