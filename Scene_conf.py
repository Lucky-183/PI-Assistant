from config import config
from play import play

init_state={
            "music_playing": False,
            "time": None,
            "user_status": "offline"
        }
init_condition={
        "Morning": {"time": (15, 15,0,47), "user_status": None},
        "Night": {"time": (0, 15,0,49), "user_status": None},
    }

def deal_condition(scene):
    if scene == "Morning":
        config.set(notify=True, time_notify=True, general_volume=0.8, music_volume=0.3)
        play('Sound/goodmorning.raw')
    elif scene == "Night":
        play('Sound/goodnight.raw')
        config.set(notify=False, time_notify=False, general_volume=0.5, music_volume=0.1)
