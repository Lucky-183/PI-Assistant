import sys
from const_config import snowboy_enable,gpio_wake_enable,use_online_recognize,music_enable,schedule_enable,use_openai,dev_enable,wlan_enable

if snowboy_enable:
    from const_config import snowboypath
    sys.path.append(snowboypath)
    from snowboy import hotwordBymic

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

if use_openai:
    import gpt
else:
    import sparkApi

import os

import arcade

from threading import Thread

import asyncio

import time

from config import config

import if_exit

import if_time

from play import play

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
    if running == True and allow_running == False:
        actived = 3
        return False
    if running == True:
        actived = 2  # 运行时激活
        print('interrupt')
    else:
        actived = 1  # 休眠激活


def admin():
    global actived, allow_running, actived, next, running, flag, chatsound, chatplayer ,times
    while (flag == 1):
        if actived == 3 or (chatsound and chatplayer and chatsound.is_playing(chatplayer) is False and running is False) :
            config.set(chat_enable=False)
        if actived == 3 or (running is False and config.get("notify_enable") is False and (actived == 1 or (next is True and chatsound and chatplayer and chatsound.is_complete(chatplayer)))):
            if actived == 3:
                print('error in chat,thread dead')
                play('Sound/exit.wav')
                os._exit(0)
            t1 = Thread(target=work)
            t1.setDaemon(True)
            config.set(chat_enable=True)

            t1.start()
            print('start new task ')
        if actived == 2:
            allow_running = False
            actived = 1
        if actived == -1:
            # interruped = True
            flag = 0
        if chatsound and chatplayer and chatsound.is_playing(chatplayer):
            if chatsound.is_complete(chatplayer):
                try:
                    chatsound.stop(chatplayer)
                    times=0
                except:
                    print('stop sound wrong in admin')
                else:
                    print('chatsound has been stoped by admin func')
            else:
                times=times+1
                if times>=170:
                    try:
                        chatsound.stop(chatplayer)
                    except:
                        print('stop sound wrong in admin(time)')
                    else:
                        print('chatsound has been stoped by admin func(time)')
                    times = 0
        time.sleep(0.5)


def work():
    global next, allow_running, running, flag, chatplayer, chatsound, actived, interruped, text, text_enable , next_enable ,manual_enable,times
    running = True
    next = True if next_enable is True else False

    if (chatplayer and chatsound and chatsound.is_playing(chatplayer)):
        try:
            print('stoping chatsound')
            chatsound.stop(chatplayer)
            times=0
        except:
            print('stop chatsound wrong')

    actived = 0
    if allow_running and ((text_enable or manual_enable) is False):
        try:
            play('Sound/ding.wav')

            print('prepare to start record')

            speechpoint.record_file()

            # audio=speechpoint.record()

            play('Sound/dong.wav')

        except Exception as e:
            print(e)
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
            print(text)
        except Exception as e:
            print(e)
            play('Sound/recoerror.wav')
            next = False
            allow_running = True
            running = False
            return None

    if allow_running:
        text_enable = False

    if allow_running:
        # 判断是否退出

        # print('in function text',text)
        if if_exit.ifend(text):
            next = False
            allow_running = True
            running = False
            config.set(chat_enable=False)
            return None

        if if_exit.ifexit(text):
            if use_openai:
                gpt.save()
            else:
                sparkApi.save()
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
                    print('stoping chatsound(if_music)')
                    chatsound.stop(chatplayer)
                    times=0
                except:
                    print('stop chatsound wrong')
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
                    print('stoping chatsound(if_time)')
                    chatsound.stop(chatplayer)
                    times=0
                except:
                    print('stop chatsound wrong')
            next = False
            allow_running = True
            running = False
            config.set(chat_enable=False)
            return None
        
    if allow_running:
        if use_openai:
            gpt.ask(text)
        try:
            if use_openai:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                #异步适配ddg
                reply = gpt.deal()
                loop.close()
            else:
                reply=sparkApi.ask(text)

        except Exception as e:

            print('error:', e)
            play('Sound/ding.wav')
            play('Sound/gpterror.wav')
            allow_running = True
            running = False
            return None
        else:
            if use_openai:
                print(reply['content'])
                config.set(answer=reply['content'])
            else:
                print(reply)
                config.set(answer=reply)

        if use_openai and reply['content'].find('结束对话') != -1:
            next = False

        if config.get("mqtt_message") is True:
            mqtt_wlan.wlan_client.send_message(config.get("answer"))
            config.set(mqtt_message=False)
            next = False
            allow_running = True
            running = False
            

    if allow_running:
        try:
            if os.path.exists('Sound/answer.wav'):
                os.remove('Sound/answer.wav')
            if use_openai:
                ssml_wav(reply['content'],'Sound/answer.wav')
            else:
                ssml_wav(reply,'Sound/answer.wav')
            print('ssml complete!')
        except Exception as e:
            print(e)
            play('Sound/ttserror.wav')
            allow_running = False
        play('Sound/ding.wav')
    if allow_running:
        chatsound = arcade.Sound('Sound/answer.wav')
        chatplayer = chatsound.play()
        time.sleep(0.5)
    print('A conversation end')
    allow_running = True
    running = False
    return None


def inter():
    global actived, text, text_enable, flag, t3, manual_enable, next_enable
    while (1):
        cmd = config.get("command")
        if cmd == 'wake':
            print('find words wake')
            actived = 1
            config.set(command='')
            continue
        elif cmd == 'get_audio_complete':
            print('find words get_audio_complete')
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
                hotwordBymic.terminate()
                config.set(wakebyhw=False, hw_started=False)  # 同时设置 hw_started 状态
            except:
                print('stop hotword_wake wrong')
            else:
                pass
            t3 = None
            next_enable = False
            config.set(command='')
            continue

        # 在 "start" 命令中
        elif snowboy_enable is True and (cmd == 'start' or (config.get("wakebyhw") is True and config.get("hw_started") is False)):
            if t3 is None:
                t3 = Thread(target=hotwordBymic.start, args=(hwcallback,))
                t3.setDaemon(True)
                t3.start()
                config.set(wakebyhw = True,hw_started=True)  # 设置 hw_started 状态
            next_enable = True
            play('Sound/hwstartsucc.wav')
            config.set(command='')
            continue
        elif cmd != '':
            print('find something in command')
            text = config.get("command")
            text_enable = True
            hwcallback()
            config.set(command='')
            print('is', text)
            continue

        time.sleep(0.5)

def exwake():
    while(1):
        GPIO.wait_for_edge(4, GPIO.RISING) 
        hwcallback()
        time.sleep(5)

def startchat():
    global t3
    t2 = Thread(target=inter)
    t2.setDaemon(True)
    t2.start()
    #os.system('/home/pi/linkbt.sh')
    if use_openai:
        gpt.read()
    else:
        sparkApi.read()
    if snowboy_enable is True and config.get("wakebyhw") is True:
        t3 = Thread(target=hotwordBymic.start, args=(hwcallback,))
        t3.setDaemon(True)
        t3.start()
    if gpio_wake_enable:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
        t4= Thread(target=exwake)
        t4.setDaemon(True)
        t4.start()
    play('Sound/ding.wav')
    play('Sound/welcome.wav')
    admin()


if __name__ == "__main__":
    admin()
