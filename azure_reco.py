
import requests
import json
import time
from const_config import azure_key
url='https://eastasia.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=zh-CN'

header={
'Accept': 'application/json;text/xml',
'Content-Type': "audio/wav; codecs=audio/pcm; samplerate=16000",
'Ocp-Apim-Subscription-Key': azure_key
}
asession=requests.session()

def recognize():
    with open('Sound/question.wav','rb') as f:
        files= {'file': f}
        for _ in range(2):
            try:
                b = asession.post(url, headers=header, files=files,timeout=12)
                # print(b.text)
                break
            except Exception as e:
                print('recognize wrong',e)
                time.sleep(3)
        f.close()
    try:
        mid=json.loads(b.text)['DisplayText']
    except:
        print('json load wrong, return none')
        mid=''
    return mid
if __name__ == "__main__":
    recognize()




