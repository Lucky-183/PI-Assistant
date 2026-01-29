import sounddevice as sd
import numpy as np
import wave
from loguru import logger
import os
from pydub import AudioSegment
from config import config

flag = 0

def play(filename, volume=config.get("general_volume")):
    """
    通用播放函数：
    - WAV（真正 WAV PCM16）直接用 wave + numpy
    - MP3 / 伪 WAV（后缀 .wav 但实际上是 MP3）用 pydub 解析
    """
    global flag
    if flag == 1:
        return
    flag = 1

    try:
        _, ext = os.path.splitext(filename)

        # 如果是 WAV 文件
        if ext.lower() == ".wav":
            # 先判断是否真 WAV
            with open(filename, "rb") as f:
                header = f.read(4)
            if header == b"RIFF":
                # 真 WAV PCM16
                with wave.open(filename, "rb") as wf:
                    samplerate = wf.getframerate()
                    channels = wf.getnchannels()
                    sampwidth = wf.getsampwidth()
                    raw_data = wf.readframes(wf.getnframes())
                    if sampwidth == 2:
                        dtype = np.int16
                    elif sampwidth == 4:
                        dtype = np.int32
                    else:
                        raise ValueError(f"Unsupported WAV sample width: {sampwidth}")
                    samples = np.frombuffer(raw_data, dtype=dtype)
                    if channels > 1:
                        samples = samples.reshape(-1, channels)
            else:
                # 后缀是 wav，但内容是 mp3
                audio = AudioSegment.from_file(filename, format="mp3")
                samplerate = audio.frame_rate
                samples = np.array(audio.get_array_of_samples())
                if audio.channels > 1:
                    samples = samples.reshape(-1, audio.channels)

        # 其他格式直接用 AudioSegment 自动识别
        else:
            audio = AudioSegment.from_file(filename)
            samplerate = audio.frame_rate
            samples = np.array(audio.get_array_of_samples())
            if audio.channels > 1:
                samples = samples.reshape(-1, audio.channels)

        # 调整音量
        samples = (samples * volume).astype(np.int16)

        # 播放
        sd.play(samples, samplerate=samplerate)
        sd.wait()

    except Exception as e:
        logger.warning(f"Error occurred while playing {filename}: {e}")
    finally:
        flag = 0
