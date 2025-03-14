import pvporcupine
from pvrecorder import PvRecorder
from const_config import porcupine_key,porcupine_keyword_name,porcupinepath
from loguru import logger
import os
porcupine_keyword_name = os.path.join(porcupinepath, porcupine_keyword_name)
porcupine = pvporcupine.create(access_key=porcupine_key, keyword_paths=[porcupine_keyword_name])
recoder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
logger.info('porcupine service is loaded')

def start(callback):

    recoder.start()
    while True:
        keyword_index = porcupine.process(recoder.read())
        if keyword_index >= 0:
            logger.info(f"Detected hotword")
            callback()

def terminate():
    recoder.stop()
    porcupine.delete()
    recoder.delete()
