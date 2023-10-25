
# 树莓派语音助手 PI-Assistant

<br>

## 💡 功能列表

- 支持多种唤醒方式：语音唤醒，消息唤醒，外设唤醒
- 语音端点检测：自动检测语音截止点
- 语音识别：支持在线与离线双模式
- 文字转语音：舒适的人声
- 接续对话：完成交互对话全程只需唤醒一次
- 支持对话中断：可在任意时刻打断对话，重新提问
- 交互接入GPT：支持聊天上下文，具有互联网搜索能力，并适时总结对话
- 聊天记忆：在程序结束后保存聊天内容，重新运行时自动加载
- 通知播报：手机上接收的消息（熄屏时）以自定义格式播报
- 音乐播放：获取QQ音乐个性推荐，支持调整音量，切换，暂停
- 音频闪避：在聊天交互/通知播报时自动减小音乐音量
- 日程设定：支持设定闹钟/倒计时，以及提醒事项
- 功能可扩展：传入自定义状态，支持自定义场景触发自定义动作

<br>

## 🎁 安装

### Python模块安装

```bash
pip install requests arcade RPi.GPIO pydub numpy wave sounddevice pymysql cn2an duckduckgo_search newspaper3k flask SpeechRecognition openai pyaudio
```

### Nodejs安装

为了使用音乐播放功能，需要安装Node.js，安装完成后可在QQMusicApi路径下运行```npm start``` 测试结果（具体使用可参考[QQMusicApi文档站](https://jsososo.github.io/QQMusicApi/#/?id=qqmusicapi)以及if_music.py）

### Mysql数据库安装

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

### Snowboy语音唤醒配置

对于树莓派4B(64bit)的系统可能不需要额外配置，其他版本需要根据情况修改snowboy文件夹的配置文件，确保其能正常运行。（录入关键词需要修改assistxiaoxiao.pmdl文件，默认唤醒词为“助手晓晓”。

<br>

## 📄 使用文档

### 常量配置

修改 const_config.py 文件夹，填入树莓派的ip，Openai的key，Azure认知服务的key（语音识别和tts都用到了，免费），代理端口，路径等。

对于QQ音乐的Cookie，直接在[网页](https://y.qq.com/)登录，复制cookie的值粘贴到cookie.txt，或者填写qq账号密码，自动获取（不一定成功）

### 变量配置

在 config.py 编辑初始参数，如果要语音唤醒，将wakebyhw改为True。

### 运行

```bash
python startApi.py
python server.py
```

语音呼叫“助手晓晓”可直接唤醒，然后语音交互

可通过```http://127.0.0.1:5000/command?words=''```直接进行交互

连接了指定外设的情况下可通过按钮/无线模块触发，按钮GPIO4高电平触发，无线模块等待后期补充开源。

语音播报功能需要手机端APP配合，APP为MacroDroid，实现过程是APP端发送相应格式的消息到```http://127.0.0.1:5000/words?words=''```，然后TTS播报出来。

具体的功能可以根据chat.py的执行逻辑以及对应文件查看使用

支持自定义扩展，在 Scene.py 中定义状态变量并设置触发场景，在场景中配置相应的动作，在 config.py 中定义开关量。在其他文件中调用修改状态变量函数时会自动回调检查是否符合场景预设，若是则执行对应动作。

<br>

## ✏️ 待实现功能

- 添加外设控制文件以及对应场景，实现光感控制灯等。

- 添加星火大模型API
