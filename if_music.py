#coding=utf-8
import requests
import json
import arcade
import time
from pydub import AudioSegment
import tts
import dealCookie
from play import play
from config import config
header={"Connection":"close"}
musicsound=None
musicplayer=None
interrupted_music=False
search=False
cookiewrong=False
startagain=False
words=''
music=requests.session()
advice = []
order=0



def musicdetect(text):
        
    global interrupted_music,words,search,startagain
    
    if text=='播放音乐。' or text=='播放歌曲。' or text=='放一首音乐。' or text=='来一首音乐。'or text=='来首音乐。' or text.find('来一首歌')!=-1 or text.find('放首歌')!=-1 or text.find('来首歌')!=-1 or text=='播放推荐音乐。' or text=='播放日推。'or text.find('继续播放')!=-1 :
        play('Sound/musicprepare.wav')
        music_en()
        print('up the music')
        startagain=True
        return True
   
    elif text.find("播放音乐")==0 or text.find('搜索音乐')!=-1 or text.find('搜索歌曲')!=-1 or text.find('播放歌曲')!=-1:
        try:
            words=text[4:]
            if words[-1]=='。':
                words=words[:-1]
            if words[0]=='，':
                words=words[1:]
            if words.find('歌手')!=-1:
                words = " ".join(words.split('的',1))
            # if words.find('的')!=-1:
            #     words=" ".join(words.split('的'))
        except:
            print('words split wrong')
            return True
        print('搜索：',words)
        interrupted_music=True
        search=True
        startagain=True
        music_en()
        return True

    elif text=='下一首。' or text =='下一首音乐。'or ((text.find('播放')!=-1 or text.find('切换')!=-1) and (text.find('下首')!=-1 or text.find('下一首')!=-1)):
        interrupted_music=True
        print('切换下一首音乐')
        startagain=True
        return True

    elif (text.find('停止')!=-1 or text.find('暂停')!=-1 or text.find('关闭')!=-1) and (text.find('音乐')!=-1 or text.find('播放')!=-1 or text.find('歌曲')!=-1)or text=='静音。'or text.find('音乐关了')!=-1:
        music_off()
        print('off the music')
        return True

    elif text.find('调整')!=-1 and (text.find('声音')!=-1 or text.find('音量')!=-1):
        try:
            if text[-1] == '。':
                config.set(music_volume=float(text[-4:-2])/100)
            print(config.get("music_volume"))
        except:
            print('words split wrong in set volume')
            return True
        return True 
    elif text.find('声音')!=-1 or text.find('音量')!=-1 :
        if text.find('大一点')!=-1 or text.find('调大')!=-1 or text.find('增加')!=-1 or text.find('提高')!=-1 :
            config.set(music_volume=config.get("music_volume")+0.1)
            print('volume',config.get("music_volume"))
            return True
        elif text.find('小一点')!=-1 or text.find('调小')!=-1 or text.find('减小')!=-1 or text.find('降低')!=-1 :
            config.set(music_volume=config.get("music_volume")-0.1)
            print('volume',config.get("music_volume"))
            return True
    return False


def music_get(url, headers):
    for _ in range(2):
        try:
            r = music.get(url, headers=headers, timeout=10)
            return r
        except Exception as e:
            print(e)
            time.sleep(5)
    play('Sound/urlwrong.wav')
    return False

def get_source_cookie():
    # print('stop in get source cookie')
    # return
    print('start get source cookie')
    dealCookie.get_cookie()
    print('complete')

def set_cookie():

    get_source_cookie()
    with open('cookie.txt', 'r') as f:
        cookie = f.read()
        f.close()
    cookiejson = {'data': cookie}
    #print('cookie is', cookie)
    print('start set new cookie')
    headers = {"content-type": 'application/json', 'Connection': 'close'}
    r = requests.post(url='http://127.0.0.1:3300/user/setCookie', json=cookiejson, headers=headers)
    r.close()

def get_cookie():
    global cookiewrong,startagain
    with open('cookie.txt', 'r') as f:
        cookie = f.read()
        f.close()
    cookiejson = {'data': cookie}
    print('cookie is', cookie)
    print('start set cookie')
    headers = {"content-type": 'application/json', 'Connection': 'close'}
    r = requests.post(url='http://127.0.0.1:3300/user/setCookie', json=cookiejson, headers=headers)
    r.close()
    if cookie_check():
        cookiewrong = False
        return True
    else:
        play('Sound/dealcookie.wav')
        set_cookie()
        play('Sound/dealcookieok.wav')
        if not cookie_check():
            print('source cookie error')# 获取资源出现错误,请检查cookie
            if cookiewrong is False:
                cookiewrong=True
                startagain=False
            return False
        else:
            return True

def cookie_check():

    r=music_get('http://127.0.0.1:3300/user/getCookie?id=1837699517',headers=header)
    for cookie in r.cookies:
        if cookie.name == 'qm_keyst':
            if cookie.expires < int(time.time()):
                print('need update cookie')
                return False
            else:
                print('cookie is normal')
                return True
    return False

def get_advice_list():

    if not cookie_check():
        if not get_cookie():
            print('cookie wrong , stop from get_adv_list')
            return

    r=music_get('http://127.0.0.1:3300/recommend/daily',headers=header)
    if  r is False:
        print('cannot get (request) ,return')
        return
    data=json.loads(r.text)
    for i in range(len(data['data']['songlist'])):
        if data['data']['songlist'][i]['pay']['payplay']==0:
            advice.append({'songname':data['data']['songlist'][i]['songname'],'singer':data['data']['songlist'][i]['singer'][0]['name'],'songmid':data['data']['songlist'][i]['songmid']})
    r.close()
    print('advice_list:',advice)

def get_radio_list():

    if not cookie_check():
        if not get_cookie():
            print('cookie wrong , stop from get_adv_list')
            return

    r=music_get('http://127.0.0.1:3300/radio?id=101',headers=header)
    if  r is False:
        print('cannot get (request) ,return')
        return
    data=json.loads(r.text)
    for i in range(len(data['data']['tracks'])):
        if data['data']['tracks'][i]['pay']['pay_play']==0:
            item={'songname':data['data']['tracks'][i]['name'],'singer':data['data']['tracks'][i]['singer'][0]['name'],'songmid':data['data']['tracks'][i]['mid']}
            advice.append(item)
            print(item)
    #print('advice_list:',advice)
    # r.close()
    # music.close()

def get_search_song(words):
    global interrupted_music, search
    interrupted_music = True
    search = True
    r = music_get(f'http://127.0.0.1:3300/search/quick?key={words}',headers=header)
    if  r is False:
        print('cannot get (request) ,return')
        return
    data = json.loads(r.text)
    for i in range(len(data['data']['song']['itemlist'])):
        print(i)
        r=music_get(f"http://127.0.0.1:3300/song/urls?id={data['data']['song']['itemlist'][i]['mid']}",headers=header)
        r.close()
        if  r is False:
            print('cannot get (request) ,return')
            return
        if json.loads(r.text)['data']!={}:
            return [data['data']['song']['itemlist'][i]['mid'],data['data']['song']['itemlist'][i]['name'],data['data']['song']['itemlist'][i]['singer']]
        else:
            print('find next')
    #interrupted_music=False
    #search=False
    #play(Musicnotfound.wav')
    #return False
    music.close()
    return get_search_song_deep(words)

def get_search_song_deep(words):
    global interrupted_music,search
    print('start deep search')
    r = music_get(f'http://127.0.0.1:3300/search?key={words}',headers=header)
    r.close()
    if  r is False:
        print('cannot get (request) ,return')
        return
    data = json.loads(r.text)
    print(data)
    for i in range(len(data['data']['list'])):
        if data['data']['list'][i]['pay']['pay_play']==0:
            return [data['data']['list'][i]['songmid'],data['data']['list'][i]['songname'],data['data']['list'][i]['singer'][0]['name']]
    interrupted_music=False
    search=False
    play('Sound/Musicnotfound.wav')
    # music.close()
    return False

def converter(a,b):
    global order
# convert wav to mp3
    try:
        audSeg = AudioSegment.from_file(a)
        audSeg.export(b, format="wav")
        return True
    except Exception as e:
        print(e)
        play('Sound/convertwrong.wav')
        order=order+1
        return False

def play_search_song(words):
    global musicsound,musicplayer,interrupted_music,search
    back=get_search_song(words) 
    print(back)
    if back==False:
        print('wrong in play_search_song ,return ')
        search=False
        return
    print(back)
    r=music_get(f'http://127.0.0.1:3300/song/url?id={back[0]}',headers=header)
    if r is False :
        print('cannot get (request) ,return')
        search=False
        return
    # r.close()
    r=json.loads(r.text)
    if r['result']==100:
        #for i in r['data']:
            #r=requests.get(url=r['data'][i])
        r=music_get(url=r['data'],headers=header)
        if r is False:
            print('cannot get (request) ,return')
            search=False
            return
        with open('Sound/music_search.mp3','wb') as file:
            file.write(r.content)
            file.close()
        r.close()
    else: 
        print('request not 100,return from play_search_song')
        search=False
        return
    converter('Sound/music_search.mp3','Sound/music_search.wav')
    print(f'来自{back[2]}的{back[1]}')
    tts.ssml_save(f'来自{back[2]}的,{back[1]}','Sound/musicnotify.raw')
    play('Sound/ding.wav')
    #来自back[2]的back[1]
    play('Sound/musicnotify.raw')
    time.sleep(2.5)
    musicsound=arcade.Sound('Sound/music_search.wav',streaming=True)
    musicplayer=musicsound.play(volume=config.get("music_volume"))
    interrupted_music=False
    search=False
    
    print('start play search song')
    music.close()

def play_advice_music(order):
    global musicsound,musicplayer,interrupted_music
    if len(advice)==0:
        print('advice is empty , return from play_adv_music')
        return

    r=music_get(f'http://127.0.0.1:3300/song/urls?id={advice[order]["songmid"]}',headers=header)
    if  r is False :
        print('cannot get (request in play_adv_music) ,return')
        return
    # r.close()
    r=json.loads(r.text)
    if r['result']==100:
        try:

            for i in r['data']:
                r=music_get(url=r['data'][i],headers=header)
            #r=music_get(url=r['data'],headers=header)
            if  r is False or r.status_code>=400:
                interrupted_music = True
                print('cannot get (request in play_adv_music_url) ,return')
                return
        except Exception as e:
            print(e,'exit')
            return 
        with open('Sound/music_adv.m4a','wb') as file:
            file.write(r.content)
            file.close()
        r.close()
    else:
        print('respones is not 100 , return from play_adv_music')
        return
    if not converter('Sound/music_adv.m4a','Sound/music_adv.wav'):
        return
    print(f"来自{advice[order]['singer']}的{advice[order]['songname']}")
    tts.ssml_save(f"来自{advice[order]['singer']}的,{advice[order]['songname']}",'Sound/musicnotify.raw')
    play('Sound/ding.wav')
    play('Sound/musicnotify.raw')
    time.sleep(2.5)
    musicsound=arcade.Sound('Sound/music_adv.wav',streaming=True)
    musicplayer=musicsound.play(volume=config.get("music_volume"))
    print('start play advice song')
    music.close()

def stop_music():
    global musicsound,musicplayer
    if musicsound and musicplayer and musicsound.is_playing(musicplayer):
        try:
            
            print('music stopping')
            musicsound.stop(musicplayer)
        except:
            print('stop sound wrong in if_musci stop func')

def admin_music():
    #if len(advice)==0:
    #    print('advice is empty ,start get list')
    #    get_advice_list()
    while order>=len(advice):
        print('adivce is equal to order ,start get list')
        get_radio_list()
    print(order)
    play_advice_music(order)
    return None

def music_en():
    config.set(MusicPlay=True)


def music_off():
    config.set(MusicPlay=False)

def watch():
    lastime = None
    times=0
    global musicsound,musicplayer,order,interrupted_music,advice,search,startagain,cookiewrong
    while(1):
        if cookiewrong :
            if not startagain:
                continue
        if config.get("MusicPlay"):
            if interrupted_music == True:
                stop_music()
                if search==True:
                    play_search_song(words)
                    times=0
                else:
                    order = order + 1
                    interrupted_music=False
                    # play('Sound/ding.wav')
                    # play(preparefornextmusic.wav')
                    times=0
                    print('prepare for next music')
                    # 正在为您准备下一首音乐
                    admin_music()
            elif musicsound and musicplayer :
                if musicsound.is_complete(musicplayer):
                    stop_music()
                    order=order+1
                    times=0
                    print('Watch : next music')
                    admin_music()
                    print('music is playing')
                elif musicsound.is_playing(musicplayer)==False:
                    musicplayer=musicsound.play(volume=config.get("music_volume"))
                times=times+1
                if times>800:
                    interrupted_music=True
                    print('music stop by time in if_musci')
                    times=0
            elif musicplayer == None:
                admin_music()
                order=order+1
                print('Watch : start play')
        else:
            stop_music()
        if musicsound and musicplayer and musicsound.is_playing(musicplayer):
            if (config.get("chat_enable") or config.get("notify_enable") or config.get("rec_enable")):
                if musicsound.get_volume(musicplayer)!=0.05:

                    musicsound.set_volume(0.05, musicplayer)
                    print('Watch: turn down the volume')
            elif musicsound.get_volume(musicplayer)!=config.get("music_volume"):
                musicsound.set_volume(config.get("music_volume"), musicplayer)
                print('Watch: turn up the volume')
        if time.localtime()[2]!=lastime:
            print('Watch : new day')
            lastime=time.localtime()[2]
            advice=[]
            order=0
        time.sleep(0.5)

if __name__=="__main__":
    order=0
    admin_music()
    time.sleep(200)
