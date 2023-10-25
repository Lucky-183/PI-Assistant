#coding=utf-8
import requests
import time
from play import play
from const_config import azure_key
url='https://eastasia.tts.speech.microsoft.com/cognitiveservices/v1'
header={
'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
'Content-Type': 'application/ssml+xml',
'Ocp-Apim-Subscription-Key': azure_key
}
dialog=requests.session()

def ssml_wav(text,filename):
    ssml_string=f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
    <voice name="zh-CN-XiaoxiaoNeural">
              <mstts:express-as role="YoungAdultFemale" style="friendly">
                {text}       </mstts:express-as>
    </voice>
</speak>'''
    content=dialog.post(url,headers=header,data=ssml_string.encode('utf-8'),timeout=8)
    #if (os.path.exists('answer.wav')):
    #    os.remove('answer.wav')
    with open(filename,'wb') as f:
        f.write(content.content)
        f.close()

text='闹钟设定失败'
filename = "Sound/failclock.wav"
def ssml_save(text,filename):
    header={
'X-Microsoft-OutputFormat': 'raw-24khz-16bit-mono-pcm',
'Content-Type': 'application/ssml+xml',
'Ocp-Apim-Subscription-Key': 'e4c4758bea374400bfae10ab165fe539'
}
    ssml_string=f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
    <voice name="zh-CN-XiaoxiaoNeural">
              <mstts:express-as role="YoungAdultFemale" style="friendly">
                {text}       </mstts:express-as>
    </voice>
</speak>'''
    for _ in range(2):
        try:
            content = dialog.post(url, headers=header,data=ssml_string.encode('utf-8'))
            with open(filename, 'wb') as f:
                f.write(content.content)
                f.close()
            return
        except Exception as e:
            print(e)
            time.sleep(5)
        play('Sound/ding.wav')


if __name__=="__main__":
    ssml_save("夜深了,祝您晚安",'Sound/goodnight.raw')

