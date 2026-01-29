import time
import tts
from config import config
from play import play
from loguru import logger
flag=0
def timedetect(text):
    global flag
    if text in ['时间。','几点了。','现在几点了？','当前时间。','现在的时间。']:
        logger.info('dectect keyword time')
        flag=1
        return True
    if text in ['日期。','今天是几号？','今天的日期。','今天几号？']:
        logger.info('dectect keyword date')
        flag=2
        return True
    return False

def notifytime():
    tts.ssml_save(f"当前时间:{time.strftime('%H:%M', time.localtime())}",'Sound/timenotify.raw')
    config.set(notify_enable=True)
    play('Sound/ding.wav')
    play('Sound/timenotify.raw')
    config.set(notify_enable=False)

def notifydate():
    tts.ssml_save(f"今天的日期:{time.strftime('%m月%d号', time.localtime())}",'Sound/timenotify.raw')
    config.set(notify_enable = True)
    play('Sound/ding.wav')
    play('Sound/timenotify.raw')
    config.set(notify_enable = False)

def admin():
    global flag
    while(1):
        if flag==1:
            notifytime()
            flag=0
        if flag==2:
            notifydate()
            flag=0
        time.sleep(1)
