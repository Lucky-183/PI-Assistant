import sounddevice as sd
import numpy as np
import wave
from config import config
import os

flag=0
def play(filename, volume=config.get("general_volume"), samplerate=16000):
    global flag
    if flag == 1:
        return
    flag=1
    _, ext = os.path.splitext(filename)
    
    # 如果文件是WAV格式
    if ext.lower() == ".wav":
        with wave.open(filename, 'rb') as wf:
            samples = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    # 如果文件是raw PCM格式
    elif ext.lower() == ".raw":
        samples = np.fromfile(filename, dtype=np.int16)
        samplerate=24000
    else:
        raise ValueError("Unsupported file type!")
    
    # 调整音量
    samples = (samples * volume).astype(np.int16)
    
    # 播放音频
    sd.play(samples, samplerate=samplerate)
    sd.wait()
    flag=0
