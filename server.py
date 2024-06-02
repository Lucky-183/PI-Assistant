#coding=utf-8
import sys
import os
import signal
import time
from loguru import logger
logger.remove()
logger.add(sys.stdout, colorize=True,  format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}", level="INFO")
logger.add('Log/PI-Assistant.log', colorize=False,  format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {file}:{line} - <level>{message}</level>", level="DEBUG")

from flask import request,Flask,jsonify,render_template
import arcade
from threading import Thread
import chat
from config import config
from const_config import music_enable,schedule_enable,udp_enable,hass_demo_enable
import if_time
import tts
from play import play
import Scene

if music_enable:
    import if_music
if schedule_enable:
    import schedule
if udp_enable:
    import udpserver

import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

notifyplayer=None
notifysound=None

app = Flask('PI-Assistant')

@app.route('/')
def index():
    editable_config = {k: config.params[k] for k in config.allow_params if k in config.params}
    return render_template('index.html', config=editable_config)

@app.route('/update_config', methods=['POST'])
def update_config():
    data = request.json
    for key, value in data.items():
        # 转换为合适的数据类型
        if isinstance(value, str):
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass
        config.set(**{key: value})
    return jsonify(success=True)

last_answer=None

@app.route('/get_answer', methods=['GET'])
def get_answer():
    global last_answer  # 使用全局变量来跟踪上一次的答案
    current_answer = config.params.get('answer', '')  # 获取当前的答案
    # 检查答案是否有变化
    if current_answer != last_answer:
        last_answer = current_answer  # 更新上一次的答案
        return jsonify(answer=current_answer)  # 发送新答案
    else:
        return jsonify(answer=None)  # 无变化时不发送答案

quick_commands = ["wake","终止程序","下一首。"]

@app.route('/get_quick_commands', methods=['GET'])
def get_quick_commands():
    return jsonify(quick_commands)

@app.route('/add_quick_command', methods=['POST'])
def add_quick_command():
    command = request.json.get('command')
    if command and command not in quick_commands:
        quick_commands.append(command)
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/remove_quick_command', methods=['POST'])
def remove_quick_command():
    index = request.json.get('index')
    if 0 <= index < len(quick_commands):
        del quick_commands[index]
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/cookie')
def chang():
    submit = request.args.get('cookie')
    logger.info(f"收到cookie：{submit}")
    with open('cookie.txt','w') as f:
        f.write(submit)
        f.close()
    return 'ok'

words=''
@app.route('/words')
def speakk():

    global words,notifyplayer,notifysound
    words = request.args.get('words')

    if config.get('Noticenotify'):
        try:
            tts.ssml_wav(words,'Sound/notify.wav')
        except:
            play('Sound/ttserror.wav')
            return 'ok'
        if config.get("chat_enable") is False and config.get("notify_enable") is False:
            config.set(notify_enable=True)
            time.sleep(0.5)
            play('Sound/ding.wav')
            notifysound = arcade.Sound('Sound/notify.wav')
            notifyplayer=notifysound.play()
    
    return 'ok'

@app.route('/get')
def send():
    if udp_enable:
        udpserver.udp_hi()
    return 'receive'

@app.route('/back')
def call():
    play('Sound/ding.wav')
    play('Sound/devconnect.wav')
    return 'ok'

@app.route('/command')
def what():
    words = request.args.get('words')
    config.set(command=words)
    return 'ok'

def signal_handler(sig, frame):
    logger.info('Shutting down...\n')
    os._exit(0)

def admin():
    global notifyplayer,notifysound
    last_time=None
    times=0
    while(1):
        if notifyplayer and notifysound and notifysound.is_playing(notifyplayer):
            if  notifysound.is_complete(notifyplayer): 
                config.set(notify_enable=False)
                try:
                    notifysound.stop(notifyplayer)
                    logger.info('stop sound in server admin')
                except:
                    logger.warning('cannot stop sound in server admin')
                times=0
                logger.info('notifysound stoped by server watch function')
            else:
                times=times+1
                if times>=8:

                    config.set(notify_enable=False)
                    try:
                        notifysound.stop(notifyplayer)
                        logger.warning('stop sound in admin by time')
                    except:
                        logger.warning('cannot stop sound in admin by time')
                    logger.info('notifysound stoped by server watch function(time)')
                    times=0

        if time.localtime()[4]==0 and config.get("timenotify") is True:
            if last_time!=time.localtime()[3]:
                logger.info('notify time')
                words=f'整点报时,已经{time.localtime()[3] if time.localtime()[3]<13 else time.localtime()[3]-12}点啦'
                try:
                    tts.ssml_wav(words,'Sound/notify.wav')
                    if config.get("chat_enable") is False and config.get("notify_enable") is False:
                        config.set(notify_enable = True)
                        play('Sound/ding.wav')
                        notifysound = arcade.Sound('Sound/notify.wav')
                        notifyplayer = notifysound.play()
                except Exception as e:
                    logger.warning(e)
                    if config.get("chat_enable") is False and config.get("notify_enable") is False:
                        play('Sound/ding.wav')
                        play('Sound/notifytime.wav')
                last_time=time.localtime()[3]

        time.sleep(2)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    t=Thread(target=chat.startchat)
    t.start()
    logger.info('Chat service started successfully')
    t2=Thread(target=admin)
    t2.start()

    if music_enable:
        t3=Thread(target=if_music.watch)
        t3.start()
        logger.info('Music service started successfully')
    
    if udp_enable:
        t4=Thread(target=udpserver.udp_server)
        t4.start()
        logger.info('Udp service started successfully')

    t5=Thread(target=if_time.admin)
    t5.start()

    if schedule_enable:
        t6=Thread(target=schedule.timer)
        t6.start()
        logger.info('Schedule service started successfully')
    
    if hass_demo_enable:
        import hass_light_demo
        t7=Thread(target=hass_light_demo.handle)
        t7.start()
        logger.info('hassApi service started successfully')

    logger.info('Startup completed , PI-Assistant is running')

    app.run(host='0.0.0.0')

