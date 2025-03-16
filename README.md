
# 树莓派语音助手 PI-Assistant

<br>

## 🗺️ 更新日志

### [2025/3/14]

- 添加跨平台的语音唤醒方案 Porcupine ，识别效果更佳
- 不涉及硬件的功能均可**在Windows上运行**，运行环境Python3.9(64bit)及以上

### [2025/2/20]

- 增加DeepSeek模型选项（由[SiliconFlow](https://cloud.siliconflow.cn/models)提供Api接口）
- 接入硅基流动（SiliconFlow）平台，系列顶尖大模型随心切换
- 模型回答修改为**流式输出**，TTS音频升级为**流式传输/播放**，对话感知延迟大幅降低
- 实现大模型调度控制设备，区分为聊天模式（流式）和标准模式（设备控制，非流式）
- 完善场景/状态配置与外设控制，用于对接模型调度
- 新增提示词入口，统一编辑，优化程序代码逻辑，增强可读性
- 更新 ``` requirement.txt ```文件以及项目文件层次结构图

<details>

<summary>更多</summary>

### [2024/6/2]

- 规范运行日志（引入loguru库）
- 新增外设端口 BCM号18（用于外接语音唤醒模块，以获得更好的唤醒体验）
- 添加Ctrl+C中断退出
- 更新README.md


### [2024/5/13]

- 增加HomeAssistant设备控制，利用HA的API实现了对其下设备的控制，并提供了一个基本示例
- 修改了文档中对场景、外设及自动化部分的语言描述，更清晰易懂


### [2024/3/12]

- 增加广域网控制支持，采用MQTT协议，实现广域网下的设备控制，消息传递
- 完善WebUI，增加快捷命令，增加回复窗口
- 完善星火API，相比GPT可能会有更好的体验
- 星火版本指向3.5，GPT版本改指向GPT-4-turbo-preview
- 适配新版本DDG搜索
- 增强设备控制通用性和稳定性，完善场景逻辑
- 删除早期APP，统一采用Web控制
- 添加requirements.txt，列出运行版本号



### [2024/2/3]

- 支持局域网外设控制（MQTT）
- 优化场景类、配置类、状态类结构
- 最小化程序支持在PC（win10）运行
- 简化代码,删除音乐模块的自动获取Cookie功能

  
### [2024/1/8]

- 解决duckduckgo联网搜索失效的问题（注意及时升级ddg库）

### [2023/12/29]

- 已支持WebUI调参，可调参数可自由选择
- 已支持讯飞星火大模型API
- 优化场景配置代码

</details>
<br>

## 💡 功能列表

- 多模型接入：可选DeepSeek/OpenAi/星火大模型等，支持聊天上下文，具有互联网搜索能力
- 可选流式生成：模型流式输出内容，TTS音频流式传输
- 支持多种唤醒方式：语音唤醒，局域网消息唤醒，外设模块唤醒，远程唤醒
- 语音端点检测：自动检测语音截止点
- 语音识别：支持在线与离线双模式
- 文字转语音：舒适的人声
- 接续对话：完成交互对话全程只需唤醒一次
- 支持对话中断：可在任意时刻打断对话，重新提问
- 聊天记忆：在程序结束后保存聊天内容，重新运行时自动加载
- 通知播报：手机上接收的消息（熄屏时）以自定义格式播报
- 音乐播放：获取QQ音乐个性推荐，支持调整音量，切换，暂停
- 音频闪避：在聊天交互/通知播报时自动减小音乐音量
- 日程设定：支持设定闹钟/倒计时，以及提醒事项
- WebUI调参：可通过电脑和手机登录网页调参
- 外设控制：支持接入自定义设备（MQTT协议），配置相关文件可实现自动化
- 自动化智能家居：传入自定义状态，支持自定义场景触发自定义动作
- 远程控制：支持广域网MQTT设备控制
- HomeAssistant：支持通过API控制HA下的设备
- 模型调度：支持向模型输入状态（模糊）控制设备，配合HA完成智能家居控制
<br>

## 🎁 安装

### Python模块安装

```bash
pip install azure-cognitiveservices-speech loguru requests arcade RPi.GPIO pydub numpy sounddevice pymysql cn2an duckduckgo_search flask SpeechRecognition openai pyaudio websocket-client paho-mqtt 
```

具体库版本可参考```requirements.txt```文件

### Azure认知服务

为了使用语音识别以及文字转语音，需要注册微软Azure，获取Azure认知服务的APIkey

### 硅基流动云服务/GPT服务/星火API

为了生成对话文本，需要注册硅基流动/OpenAI/讯飞星火账号（三选一），并获取APIkey

### Nodejs安装(可选)

为了使用音乐播放功能，需要安装Node.js，默认qq号 1234567 ，修改 bin/config.js 为自己的QQ号 , 安装完成后可在QQMusicApi路径下运行```npm start``` 测试结果（具体使用可参考[QQMusicApi文档站](https://jsososo.github.io/QQMusicApi/#/?id=qqmusicapi)以及if_music.py）

### Mysql数据库安装(可选)

为了实现日程提醒功能，需要安装Mysql数据库，安装并后台运行，对应schedule.py文件，以下是一些参考命令：

```mysql
show databases;
create database schedule;
use schedule;
create table main (id int(11)primary key, time int(11),content varchar(50));
alter table main modify column id int(11) AUTO_INCREMENT;
CREATE USER 'remote'@'%' IDENTIFIED BY '123456';
GRANT ALL ON schedule.* TO 'remote'@'%';
```

### Snowboy语音唤醒配置(可选)

对于树莓派4B(64bit)的系统可能不需要额外配置，其他版本需要根据情况修改snowboy文件夹的配置文件，确保其能正常运行。（录入关键词需要修改assistxiaoxiao.pmdl文件，默认唤醒词为“助手晓晓”。）


### 场景、外设及自动化配置(可选)

当前实现的所有参数监听及修改都基于多线程下的循环执行（轮询），因此可以通过在 ```server.py``` 添加新的线程插入你的外设控制文件。具体步骤为：在 ```config.py``` 中添加变量，编写专用外设控制文件，在专用外设控制文件监听（轮询）变量，执行自定义动作。在任意文件中调用 ```config.set()``` 即可触发动作。

例如，在 ```server.py``` 新增一个线程用于处理控制HomeAssistant设备的消息 ```t7``` ，在 ```config.py``` 中定义变量 ```"HA_light_demo": False```，在 ```hass_light_demo.py``` 中处理消息和执行动作。如果要增加语音控制，在 ```if_devControl.py``` 中添加对应的语音指令和 ```config.set()``` 即可。

支持外接无线设备，作为设备的数据流转和控制中心，可达到极高的可扩展性。可在 ```config.py``` 中添加外设变量，在 ```dev_control.py``` 中定义设备类型，订阅主题和推送主题，同时，在wifi设备上（例如esp32）配置对应的主题，在任意文件中调用 ```config.set()``` 即可触发外设动作（将会发送值到预先定义的主题中，外设接收此值响应动作）。

进一步的，实现自动化，则在 ```Scene_conf.py``` 中定义状态变量并设置触发场景、配置相应的动作。调用修改状态变量函数 ```status_manager.set_status()``` 时会自动回调检查是否符合场景预设，若是则执行对应动作。（注：无线外设扩展现仅支持MQTT协议设备）

<details>
<br>
外设通讯协议为MQTT，在树莓派上安装mosquito服务器，用户名和密码分别设置为 pi，123456。配置参考如下：

/etc/mosquitto/mosquitto.conf

```
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd
```

设备分为输入设备（如传感器）和输出设备（如开关），以下描述了外设控制的两种数据流动：

- 输入设备（传感器）数据→状态管理器→场景管理器→配置管理器→输出设备（开关、灯）

此控制方案用于自动化控制，传感器的值会改变状态管理器的状态量，进而触发场景检测，满足对应场景后调用配置管理器的接口，控制设备。

- 控制命令（语音）→配置管理器→输出设备（开关、灯）

此控制方案用于手动控制，通过文字指令或语音指令直接修改配置管理器的变量，控制设备。

外设控制配置文件包括以下几个文件：```dev_control.py```(定义所有设备) ,```config.py```（定义输出设备） ,```Scene_conf.py```(定义输入设备以及场景)

文件中提供了一个示例，```sensor_demo```为输入设备，```dev_demo```作为输出设备，当```sensor_demo```发送```True（False）```时，```dev_demo```点亮（关闭）板载LED。硬件采用Esp32，相关的硬件代码提供在```mqtt_demo```文件夹。

代码设计有反馈机制，输出设备在接收到信息后需要有ACK，否则树莓派会认为此次控制不成功。
</details>

### 大模型调度控制设备(可选)

修改 ``` const_config.py ``` 中的 ``` chat_or_standard ```为 ```False ```，在 ``` config.py ``` 以及 ``` Scene_conf.py ``` 中添加设备，程序将同时发送用户消息以及```输入设备```的状态到大语言模型，返回一段文字以及命令，文字用于反馈用户，命令用于控制```可控设备```，详见``` prompt_and_deal.py ```

### 广域网MQTT配置(可选)

采用中国移动ONENet的MQTT服务器，实现在广域网下与家庭助手通信。

PI-Assistant共订阅三个topic：Input（实现对输入设备数据的改写）、Output（实现对输出设备的控制）、message_pi（用于消息的传递，即远程通信）

PI-Assistant会将 message_pi 传来的消息进过和本地消息几乎同样的处理，而后将返回结果发送到名为 “message_endpoint" 的主题上。

例如，在MQTT手机端Publish主题为 “Output”，内容为```"dev_demo:True”```的消息，即可打开设备```dev_demo```的Led灯。提前订阅 “message_endpoint”，向主题 message_pi 发送```“你好”```，稍后将会在 “message_endpoint” 上收到```“你好，我是晓晓智能助手...”```，具体实现参考 ```mqtt_wlan.py```以及```chat.py```。

中国移动MQTT服务器的配置方法：onenet -> 开发者中心 -> 全部产品服务 -> 多协议接入 -> MQTT（旧版）-> 添加产品 -> 添加设备 

<br>

## 📄 使用文档

### 常量配置

修改 ``` const_config.py ``` 文件夹，Openai的key，Azure认知服务的key（语音识别和tts都用到了，免费），代理端口，路径，相应功能的开启关闭等。可在 ``` prompt_and_deal.py ```中修改提示词。

对于QQ音乐的Cookie，直接在[网页](https://y.qq.com/)登录，复制cookie的值粘贴到cookie.txt。

### 变量配置

在 config.py 编辑初始参数，如果要语音唤醒，将wakebyhw改为True。

### 运行

```bash
python startApi.py #音乐服务
python server.py #主程序
```

语音呼叫“助手晓晓”可直接唤醒，然后语音交互

在APP上配置IP后发送消息交互，也可通过```http://语音助手ip:5000/command?words=''```直接进行交互

连接了指定外设的情况下可通过按钮/无线模块触发，按钮GPIO7(BCM:4)高电平触发。 无线模块开源链接：https://oshwhub.com/ghgjkh/simple-wake 

语音播报功能需要手机端APP配合，APP为MacroDroid，实现过程是APP端发送相应格式的消息到```http://语音助手ip:5000/words?words=''```，然后TTS播报出来。

具体的功能可以根据chat.py的执行逻辑以及对应文件查看使用



### 运行时调参

可使用网页端在程序运行时调参,地址为 http://ip:5000 


### 文件层次结构

![p1](https://github.com/Lucky-183/PI-Assistant/blob/master/arch.png)

<br>


## ✏️ 待实现功能


- 创建HA语音助手接口，使其具备轻松控制所有家具的能力

- ‘场景’控制方案重写（描述）为‘自动化’控制方案

- OpenAi/星火模型逐步转向流式输出

- 增加语音合成及识别接口

~~低功耗BLE外设硬件开发~~

~~未联网下自动切换为离线语音识别~~

<br>

## 🎉 其他

欢迎提交Issue与Pull Request

