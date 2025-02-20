# 用到的端口 3306 mysql 3300 音乐接口 5000 网络交互 6666 udp服务

use_deepseek=True
sfapikey=''

use_openai=False #True则使用openai
openapikey='' #gpt-key

use_spark=False
sparkapi_appid=''
sparkapi_secret=''
sparkapi_key=''

#####以上模型提供方三选一,True选择对应的模型,需要填写key######

chat_or_standard=True #采用聊天模式还是标准模式（家庭助手），True为聊天模式（采用流式），详见 prompt_and_deal.py
use_online_recognize=True #是否采用线上语音识别（效果好，针对优化）
azure_key=''   #Azrue tts recog
proxy= {'http':'http://127.0.0.1:10810',
        'https':'http://127.0.0.1:10810'} #openai以及duckduckgo的代理
snowboy_enable=False #是否加载snowboy模块，需提前安装好
snowboypath="/home/pi/xiaoxiao/snowboy" #snowboy位置（如果开启snowboy）
gpio_wake_enable=False  #按键唤醒，如果相应引脚接有外设的情况下开启
music_enable=False  #是否开启音乐功能(需要qq音乐的cookie,并启动QQMusicAPI服务)
qqmusicpath='/home/pi/xiaoxiao/QQMusicApi' #MusicApi位置(如果开启音乐模块)
qqid=''  #填写登录QQ音乐的QQ号(如果开启音乐模块,必填)
dev_enable=False  #是否开启外设控制功能(需要安装mosquito服务器，配置对应外设)
wlan_enable=False  #是否开启广域网控制
schedule_enable=False #是否开启日程提醒功能(需要配置mysql)
udp_enable=False #是否开启无线模块外设唤醒(没有无线模块就不用打开)
hass_demo_enable=False #用于演示HomeAssistant的交互，需要配置HomeAssistant。
UdpbroadcastAdd='192.168.31.255' #UDP广播地址，用于使用无线模块外设唤醒助手


