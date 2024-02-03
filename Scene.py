import threading
from datetime import datetime
from Scene_conf import init_state,init_condition,deal_condition

class StatusManager:
    def __init__(self, callback,states):
        self.states = states
        self.callback = callback
        self._start_time_updater()

    def _start_time_updater(self):
        self._update_time()
        threading.Timer(30, self._start_time_updater).start()

    def _update_time(self):
        self.states["time"] = datetime.now()
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
    def __init__(self, scene_conditions):
        self.scene_conditions = scene_conditions
        self.current_scene = "Unknown Scene"

    def check_scenes(self, states):
        for scene, conditions in self.scene_conditions.items():
            if self._scene_match(states, conditions):
                if scene != self.current_scene:
                    self.current_scene = scene
                    return scene
                return
        
        if not any(self._scene_match(states, cond) for cond in self.scene_conditions.values()):
            if self.current_scene != "Unknown Scene":
                self.current_scene = "Unknown Scene"
                return "Unknown Scene"

        return None

    def _scene_match(self, states, conditions):
        for key, value in conditions.items():
            state_value = states.get(key)
            if state_value is None:
                return False
            if isinstance(value, (list, tuple)):
                # 当条件值是一个范围（例如，元组或列表）
                if key == "time":
                    start_hour, end_hour, start_minute, end_minute = value
                    current_hour, current_minute = state_value.hour, state_value.minute

                    if start_hour > end_hour:  # 跨越午夜
                        if (current_hour > end_hour and current_hour < start_hour) or \
                                (current_hour == start_hour and current_minute < start_minute) or \
                                (current_hour == end_hour and current_minute >= end_minute):
                            return False
                    else:  # 不跨越午夜
                        if (current_hour < start_hour) or (current_hour > end_hour) or \
                                (current_hour == start_hour and current_minute < start_minute) or \
                                (current_hour == end_hour and current_minute >= end_minute):
                            return False
                else:
                    # 通用范围比较
                    if not (value[0] <= state_value <= value[1]):
                        return False
            else:
                # 当条件值是一个特定值
                if value is not None and state_value != value:
                    return False
        return True


def on_status_change(states):
    scene = scene_manager.check_scenes(states)
    if scene:
        deal_condition(scene)

        with open("Log/scene_changes.txt", "a") as f:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{current_time} - Scene changed to: {scene}\n")

        print(f"Current scene: {scene}")
    else:
        pass


scene_manager=SceneManager(init_condition)
status_manager = StatusManager(callback=on_status_change,states=init_state)


