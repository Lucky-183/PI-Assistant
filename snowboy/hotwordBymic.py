import snowboydecoder
import sys
import signal
import os
from loguru import logger
interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

def callback():
    print('hi')
#if len(sys.argv) == 1:
#    print("Error: need to specify model name")
#    print("Usage: python demo.py your.model")
#    sys.exit(-1)

model = '/home/pi/xiaoxiao/snowboy/assistxiaoxiao.pmdl'

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.4,audio_gain=3)
logger.info('Snowboy service is loaded')
def start(callback):
    
    detector.start(detected_callback=callback,
               interrupt_check=interrupt_callback,
               sleep_time=0.02)

def terminate():
    detector.terminate()
    return


