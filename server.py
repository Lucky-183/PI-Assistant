#coding=utf-8
import time
from flask import request
from flask import Flask
import arcade
from threading import Thread
import chat
from config import config
import if_music
import if_time
import udpserver
import schedule
import tts
from play import play
import Scene
notifyplayer=None
notifysound=None

global status
status='1'
words=''
app = Flask(__name__)

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
    
   #print(sys.path) 
    t=Thread(target=chat.startchat)
    #t.setDaemon(True)
    t.start()
    t2=Thread(target=admin)
    #t2.setDaemon(True)
    t2.start()
    t3=Thread(target=if_music.watch)
    #t3.setDaemon(True)
    t3.start()
    t4=Thread(target=udpserver.udp_server)
    t4.start()
    t5=Thread(target=if_time.admin)
    t5.start()
    t6=Thread(target=schedule.timer)
    t6.start()
    app.run(host='0.0.0.0')
    

        # server = pywsgi.WSGIServer(('0.0.0.0', 80), app)
        # server.serve_forever()
