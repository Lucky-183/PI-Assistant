# 用到的端口 3306 mysql 3300 音乐接口 5000 网络交互 6666 udp服务
address = "192.168.31.3" #本机地址
openapikey='' #gpt-key
use_online_recognize=True #是否采用线上语音识别（效果好，针对优化）
azure_key=''   #Azrue tts recog
UdpbroadcastAdd='192.168.31.255' #UDP广播地址，用于使用外设唤醒助手
proxy= {'http':'http://127.0.0.1:10810',
        'https':'http://127.0.0.1:10810'} #gpt以及duckduckgo的代理
snowboy_enable=False #是否加载snowboy模块，需提前安装好
gpio_wake_enable=False  #按键唤醒，如果相应引脚接有外设的情况下开启
snowboypath="/home/pi/xiaoxiao/snowboy" #snowboy位置（如果开启snowboy）
qqmusicpath='/home/pi/xiaoxiao/QQMusicApi' #MusicApi位置
qqid=''  #此两项用于QQ音乐Cookie获取,具体对应dealCookie文件,可不填
qqpw=''
