import sys
from const_config import snowboy_enable,gpio_wake_enable,use_online_recognize,\
    music_enable,schedule_enable,use_openai,dev_enable,wlan_enable,\
    use_spark,use_deepseek,chat_or_standard,porcupine_enable

if snowboy_enable:
    from const_config import snowboypath
    sys.path.append(snowboypath)
    from snowboy import hotwordBymic
elif porcupine_enable:
    from const_config import porcupinepath
    sys.path.append(porcupinepath)
    from Porcupine import porcupine

if gpio_wake_enable:
    import RPi.GPIO as GPIO

if use_online_recognize:
    import azure_reco
else:
    from voskReco import vosk_reco

if music_enable:   
    import if_music

if schedule_enable:
    import schedule

if dev_enable:
    import dev_control
    import if_devControl

if wlan_enable:
    import mqtt_wlan

import speechpoint

from tts import ssml_wav

import prompt_and_deal

if use_deepseek:
    if chat_or_standard:
        import deepseek_stream_with_tts
    else:
        import deepseek
elif use_openai:
    import openai
    import asyncio
elif use_spark:
    import sparkApi

import os

import arcade

from threading import Thread

import time

from config import config

import if_exit

import if_time

from play import play

from loguru import logger

chatsound = None
chatplayer = None
next = False
next_enable=True
actived = 0
allow_running = True
flag = 1
running = False
text_enable = False
text = ''
t3 = None
manual_enable=False

times=0

def hwcallback():
    global running, actived, allow_running
    # 根据程序运行状态设置不同的激活状态
    logger.info('HotWord triggered')
    if running and not allow_running:
        actived = 3  # 多次唤醒造成的错误标志位
        return False

    if running:
        actived = 2  # 运行时激活
        # 运行时激活停止播放声音(流式)
        if use_deepseek and chat_or_standard is True:
            deepseek_stream_with_tts.tts_manager.stop_tts()
        logger.warning('Conversation was interrupted')
    else:
        actived = 1  # 休眠激活


def admin():
    global actived, allow_running, actived, next, running, flag, chatsound, chatplayer ,times
    
    while flag == 1 :

        # 如果是actived为3,程序无法处理,直接退出
        if actived == 3: 
            logger.error('Error in chat, The program will exit soon')
            play('Sound/exit.wav')
            os._exit(0)

        # 判断是否有声音正在播放(非流式)
        is_sound_playing = chatsound and chatplayer and chatsound.is_playing(chatplayer)
        # 判断声音是否播放完成(非流式)
        is_sound_playing_complete = chatsound and chatplayer and chatsound.is_complete(chatplayer)

        #释放chat占用的语音
        if not is_sound_playing and not running :
            config.set(chat_enable=False) 
        
        # 处理接续对话
        if (not running and not config.get("notify_enable") and 
            (actived == 1 or (next is True and is_sound_playing_complete) or 
             (next is True and use_deepseek and chat_or_standard and deepseek_stream_with_tts.tts_manager.tts_task
              and deepseek_stream_with_tts.tts_manager.tts_task.get()))):  #播放完成返回信息(流式)
            
            if use_deepseek and chat_or_standard is True: #为deepseek模型添加延时
                time.sleep(2)
            
            t1 = Thread(target=work)
            t1.setDaemon(True)
            config.set(chat_enable=True)
            t1.start()
            logger.info('start new conversation')

        # 程序运行状态修改
        if actived == 2:        
            allow_running = False
            actived = 1

        # 提供函数终止的功能
        if actived == -1:
            # interruped = True
            flag = 0

        # 处理正在播放的声音,主要为异常处理 (非流式)
        if is_sound_playing:
            if chatsound.is_complete(chatplayer):
                try:
                    chatsound.stop(chatplayer)
                    times=0
                except:
                    logger.warning('stop sound wrong in chat')
                else:
                    logger.info('chatsound has been stoped by admin func in chat')
            else:
                times=times+1
                if times>=170:
                    try:
                        chatsound.stop(chatplayer)
                    except:
                        logger.warning('stop sound wrong in chat(time)')
                    else:
                        logger.info('chatsound has been stoped by admin func in chat(time)')
                    times = 0
        time.sleep(0.5)


def work():
    global next, allow_running, running, flag, chatplayer, chatsound, actived, interruped, text, text_enable , next_enable ,manual_enable,times
    running = True
    next = True if next_enable is True else False

    # 停止正在播放的声音(非流式)
    if (chatplayer and chatsound and chatsound.is_playing(chatplayer)):
        try:
            logger.info('stoping chatsound')
            chatsound.stop(chatplayer)
            times=0
        except:
            logger.warning('stop chatsound wrong')
    
    actived = 0
    if allow_running and ((text_enable or manual_enable) is False):
        try:
            play('Sound/ding.wav')

            logger.info('prepare to start record')

            speechpoint.record_file()

            # audio=speechpoint.record()

            play('Sound/dong.wav')

        except Exception as e:
            logger.warning(e)
            play('Sound/ding.wav')
            play('Sound/quit.wav')
            next = False
            allow_running = True
            running = False
            return None

    if allow_running:
        manual_enable = False

    if allow_running and ( text_enable is False ):
        try:
            if use_online_recognize:
                text = azure_reco.recognize()
            else:    
                text = vosk_reco.recognize()+'。'
            logger.info(f"Recongnize result:{text}")
        except Exception as e:
            logger.warning(e)
            play('Sound/recoerror.wav')
            next = False
            allow_running = True
            running = False
            return None

    if allow_running:
        text_enable = False

    if allow_running:
        # 判断是否退出

        if if_exit.ifend(text):
            next = False
            allow_running = True
            running = False
            config.set(chat_enable=False)
            return None

        if if_exit.ifexit(text):
            if use_openai:
                openai.save()
            elif use_spark:
                sparkApi.save()
            elif use_deepseek:
                if chat_or_standard:
                    deepseek_stream_with_tts.save()
                else:
                    deepseek.save()
            flag = 0
            next = False
            allow_running = True
            running = False
            os._exit(0)
            return None
    
    if allow_running:

        if schedule_enable and schedule.if_schedule(text):
            next = False
            allow_running = True
            running = False
            config.set(chat_enable=False)
            return None

    if allow_running:
        if music_enable and if_music.musicdetect(text):
            if (chatplayer and chatsound and chatsound.is_playing(chatplayer)):
                try:
                    logger.info('stoping chatsound(if_music)')
                    chatsound.stop(chatplayer)
                    times=0
                except:
                    logger.warning('stop chatsound wrong')
            next = False
            allow_running = True
            running = False
            config.set(chat_enable=False)
            return None

    if allow_running:
        if dev_enable and if_devControl.detect(text):
            next = False
            allow_running = True
            running = False
            config.set(chat_enable=False)
            return None
        
    if allow_running:
        if if_time.timedetect(text):
            if (chatplayer and chatsound and chatsound.is_playing(chatplayer)):
                try:
                    logger.info('stoping chatsound(if_time)')
                    chatsound.stop(chatplayer)
                    times=0
                except:
                    logger.warning('stop chatsound wrong')
            next = False
            allow_running = True
            running = False
            config.set(chat_enable=False)
            return None
        
    if allow_running:

        try:
            reply=prompt_and_deal.send(text)

        except Exception as e:

            logger.error(f'GPT error:{e}')
            play('Sound/ding.wav')
            play('Sound/gpterror.wav')
            allow_running = True
            running = False
            return None
        else:
            # 保存对话记录,发送至网页端,deepseek为流式回复,在其文件中
            if use_openai:
                logger.info(reply['content'])
                config.set(answer=reply['content'])
            else:
                logger.info(reply)
                config.set(answer=reply)

        if use_openai and reply['content'].find('结束对话') != -1:
            next = False

        if config.get("mqtt_message") is True:
            mqtt_wlan.wlan_client.send_message(config.get("answer"))
            config.set(mqtt_message=False)
            next = False
            allow_running = True
            running = False
            
        if use_deepseek and chat_or_standard and deepseek_stream_with_tts.tts_manager.tts_task:
            deepseek_stream_with_tts.tts_manager.tts_task.get()

    if allow_running and not (use_deepseek and chat_or_standard):
        try:
            if os.path.exists('Sound/answer.wav'):
                os.remove('Sound/answer.wav')
            if use_openai:
                ssml_wav(reply['content'],'Sound/answer.wav')
            else:
                ssml_wav(reply,'Sound/answer.wav')
            logger.info('tts complete!')
        except Exception as e:
            logger.warning(e)
            play('Sound/ttserror.wav')
            allow_running = False
        play('Sound/ding.wav')

    if allow_running and not (use_deepseek and chat_or_standard):
        chatsound = arcade.Sound('Sound/answer.wav')
        chatplayer = chatsound.play()
        time.sleep(0.5)

    logger.info('A conversation end')
    allow_running = True
    running = False
    return None


#交互功能
def inter():
    global actived, text, text_enable, flag, t3, manual_enable, next_enable
    while (1):
        cmd = config.get("command")
        if cmd == 'wake':
            logger.info('find words wake')
            actived = 1
            config.set(command='')
            continue
        elif cmd == 'get_audio_complete':
            logger.info('find words get_audio_complete')
            manual_enable=True
            next_enable=False
            hwcallback()
            config.set(command='')
            continue
        elif cmd == 'shutdown':
            flag = 0
            config.set(command='')
            continue
        elif cmd == 'stop' or (config.get("wakebyhw") is False and config.get("hw_started") is True):
            try:
                if snowboy_enable:
                    hotwordBymic.terminate()
                elif porcupine_enable:
                    porcupine.terminate()
                config.set(wakebyhw=False, hw_started=False)  # 同时设置 hw_started 状态
            except:
                logger.warning('stop hotword_wake wrong')
            else:
                pass
            t3 = None
            next_enable = False
            config.set(command='')
            continue

        # 在 "start" 命令中
        elif (snowboy_enable or porcupine_enable) is True and (cmd == 'start' or (config.get("wakebyhw") is True and config.get("hw_started") is False)):
            if t3 is None:
                if snowboy_enable:
                    t3 = Thread(target=hotwordBymic.start, args=(hwcallback,))
                elif porcupine_enable:
                    t3 = Thread(target=porcupine.start, args=(hwcallback,))
                t3.setDaemon(True)
                t3.start()
                config.set(wakebyhw = True,hw_started=True)  # 设置 hw_started 状态
            next_enable = True
            play('Sound/hwstartsucc.wav')
            config.set(command='')
            continue
        elif cmd != '':
            logger.info('Find something in command')
            text = config.get("command")
            text_enable = True
            hwcallback()
            config.set(command='')
            logger.info(f'The command is {text}')
            continue

        time.sleep(0.5)

def exwake_button():
    while(1):
        GPIO.wait_for_edge(4, GPIO.RISING)
        hwcallback()
        logger.info('Wake by physical button')
        time.sleep(5)

def exwake_dev():
    while(1):
        GPIO.wait_for_edge(18, GPIO.RISING)
        hwcallback()
        logger.info('Wake by Peripherals')
        time.sleep(5)

def startchat():
    global t3
    t2 = Thread(target=inter)
    t2.setDaemon(True)
    t2.start()
    #os.system('/home/pi/linkbt.sh')
    if use_openai:
        openai.read()
    elif use_deepseek:
        if chat_or_standard:
            deepseek_stream_with_tts.read()
        else:
            deepseek.read()
    elif use_spark:
        sparkApi.read()
    if (snowboy_enable or porcupine_enable) is True and config.get("wakebyhw") is True:
        if snowboy_enable:
            t3 = Thread(target=hotwordBymic.start, args=(hwcallback,))
        elif porcupine_enable:
            t3 = Thread(target=porcupine.start, args=(hwcallback,))
        t3.setDaemon(True)
        t3.start()
    if gpio_wake_enable:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(18,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
        t4= Thread(target=exwake_button)
        t4.setDaemon(True)
        t4.start()
        t5= Thread(target=exwake_dev)
        t5.setDaemon(True)
        t5.start()

    play('Sound/ding.wav')
    play('Sound/welcome.wav')
    admin()


if __name__ == "__main__":
    admin()
