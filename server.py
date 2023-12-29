#coding=utf-8
import time
from flask import request
from flask import Flask
from flask import jsonify
from flask import render_template
import arcade
from threading import Thread
import chat
from config import config
from const_config import music_enable,schedule_enable,udp_enable

if music_enable:
    import if_music
if schedule_enable:
    import schedule
if udp_enable:
    import udpserver

import if_time
import tts
from play import play
import Scene

notifyplayer=None
notifysound=None

global status
status='1'
words=''
app = Flask(__name__)

from flask import jsonify

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

@app.route('/cookie')
def chang():
    submit = request.args.get('cookie')
    print(submit)
    with open('cookie.txt','w') as f:
        f.write(submit)
        f.close()
    return 'ok'

@app.route('/status')
def statu():
    global status
    return status

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
                    print('stop sound in server watch')
                except:
                    print('wrong stop in admin')
                times=0
                print('notifysound stoped by server watch function')
            else:
                times=times+1
                if times>=8:

                    config.set(notify_enable=False)
                    try:
                        notifysound.stop(notifyplayer)
                        print('stop sound in admin by time')
                    except:
                        print('wrong stop in admin')
                    print('notifysound stoped by server watch function(time)')
                    times=0

        if time.localtime()[4]==0 and config.get("timenotify") is True:
            if last_time!=time.localtime()[3]:
                print('notify time')
                words=f'整点报时,已经{time.localtime()[3] if time.localtime()[3]<13 else time.localtime()[3]-12}点啦'
                try:
                    tts.ssml_wav(words,'Sound/notify.wav')
                    if config.get("chat_enable") is False and config.get("notify_enable") is False:
                        config.set(notify_enable = True)
                        play('Sound/ding.wav')
                        notifysound = arcade.Sound('Sound/notify.wav')
                        notifyplayer = notifysound.play()
                except Exception as e:
                    print(e)
                    if config.get("chat_enable") is False and config.get("notify_enable") is False:
                        play('Sound/ding.wav')
                        play('Sound/notifytime.wav')
                last_time=time.localtime()[3]

        time.sleep(2)

if __name__ == '__main__':
    
    t=Thread(target=chat.startchat)
    t.start()
    t2=Thread(target=admin)
    t2.start()

    if music_enable:
        t3=Thread(target=if_music.watch)
        t3.start()
    
    if udp_enable:
        t4=Thread(target=udpserver.udp_server)
        t4.start()

    t5=Thread(target=if_time.admin)
    t5.start()

    if schedule_enable:
        t6=Thread(target=schedule.timer)
        t6.start()

    app.run(host='0.0.0.0')
