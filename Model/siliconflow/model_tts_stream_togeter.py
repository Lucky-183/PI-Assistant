import requests
import time
import os
import pickle
import json
import azure.cognitiveservices.speech as speechsdk
from const_config import sfapikey ,azure_key
from loguru import logger
import threading
import pyaudio
# DeepSeek API 配置
url = "https://api.siliconflow.cn/v1/chat/completions"
key = sfapikey  # 请替换为你的 DeepSeek API Key

# 全局对话记录，保存所有的对话消息（包括系统、用户和 AI 回复）
messages = []
tts_task=None


def stop_tts():
    global tts_task
    logger.info('Start stop tts')
    speech_synthesizer.stop_speaking_async()  # Stop TTS immediately
    stop_event.set()

    if tts_task:
        result = tts_task.get()
        logger.info('Stop audio complete, Stop flag reset')

    stop_event.clear()


# 创建一个事件，用于控制停止
stop_event = threading.Event()

# 自定义音频输出流回调类
class CustomPushStreamCallback(speechsdk.audio.PushAudioOutputStreamCallback):
    def __init__(self):
        super().__init__()
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = self.pyaudio_instance.open(format=pyaudio.paInt16,
                                                 channels=1,
                                                 rate=16000,
                                                 output=True,
                                                 frames_per_buffer=8192)

    def write(self, buffer: memoryview) -> int:
        if stop_event.is_set():
            logger.debug('stoping audio')
            return 0  # 停止写入音频数据
        self.stream.write(buffer.tobytes())
        return len(buffer)

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio_instance.terminate()
        print("音频流已关闭。")


# Azure TTS 配置
speech_config = speechsdk.SpeechConfig(
    endpoint="wss://eastasia.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
    subscription=azure_key)
speech_config.speech_synthesis_voice_name = "zh-CN-XiaoxiaoNeural"

# 创建自定义音频输出流
custom_callback = CustomPushStreamCallback()
audio_output_stream = speechsdk.audio.PushAudioOutputStream(custom_callback)
audio_config = speechsdk.audio.AudioOutputConfig(stream=audio_output_stream)

speech_synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config,
    audio_config=audio_config
)
# speech_synthesizer.synthesizing.connect(lambda evt: print("[audio]", end=""))

# set timeout value to bigger ones to avoid sdk cancel the request when GPT latency too high
properties = dict()
properties["SpeechSynthesis_FrameTimeoutInterval"] = "100000000"
properties["SpeechSynthesis_RtfTimeoutThreshold"] = "10"
speech_config.set_properties_by_name(properties)


def init_system():
    """
    初始化系统对话，添加系统提示。
    """
    global messages
    messages = []
    system_message = {
        "role": "system",
        "content": (
            "你是一个家居智能助手，名为‘晓晓’。请充分扮演此角色，给出简洁、准确的回答。"
            "当用户输入为空或无意义时，请回复‘结束对话’。"
            f" 时间:[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]，地点:中国陕西省西安市。"
        )
    }
    messages.append(system_message)


def chat_request_stream():
    """
    调用 DeepSeek API 以流式方式获取 AI 回复，并传输至 Azure TTS 进行语音合成。
    """
    global messages,tts_task
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Pro/deepseek-ai/DeepSeek-V3",
        "messages": messages,
        "stream": True,
        "max_tokens": 512,
        "stop": ["null"],
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"}
    }

    # try:
    response = requests.post(url, headers=headers, json=payload, stream=True)
    if response.status_code == 200:
        ai_response = ""
        total_tokens = 0

        # 创建 TTS 输入流
        tts_request = speechsdk.SpeechSynthesisRequest(
            input_type=speechsdk.SpeechSynthesisRequestInputType.TextStream)
        tts_task = speech_synthesizer.speak_async(tts_request)
        # result=tts_task.get()      #阻塞直到音频完成

        for chunk in response.iter_lines():
            if chunk:
                decoded_chunk = chunk.decode('utf-8').strip()
                if decoded_chunk.startswith("data: "):
                    try:
                        json_data = json.loads(decoded_chunk[6:])
                        if "choices" in json_data and len(json_data["choices"]) > 0:
                            content = json_data["choices"][0]["delta"].get("content", "")
                            print(content, end='', flush=True)
                            ai_response += content

                            #tts-stream
                            if content.strip():
                                tts_request.input_stream.write(content)

                        if "usage" in json_data:
                            total_tokens = json_data["usage"].get("total_tokens", 0)
                    except json.JSONDecodeError:
                        continue

        # 关闭 TTS 输入流
        tts_request.input_stream.close()
        # if not stop_flag:
        #     result = tts_task.get()

        # 将 AI 回复存入上下文
        messages.append({"role": "assistant", "content": ai_response})

        # 监测 token 数，清理早期对话
        if len(messages) > 1 and total_tokens > 600:
            removed = messages.pop(1)
            logger.warning(f"已移除历史记录: {removed}")
            if len(messages) > 1:
                removed = messages.pop(1)
                logger.warning(f"已移除历史记录: {removed}")
    else:
        print(f"请求失败，状态码: {response.status_code}")
    # except Exception as e:
    #     print(f"请求出错: {str(e)}")


def ask(user_input):
    """
    处理用户输入，更新对话记录，并使用流式方式返回 AI 回复。
    """
    global messages
    messages.append({"role": "user", "content": user_input})
    chat_request_stream()


def save():
    """
    将当前对话记录保存到本地文件。
    """
    if os.path.exists('message.data'):
        os.remove('message.data')
    with open("message.data", 'wb+') as f:
        pickle.dump(messages, f)
    logger.info("对话记录已保存。")


def read():
    """
    从本地文件加载之前保存的对话记录。
    """
    global messages
    if os.path.exists('message.data'):
        with open('message.data', "rb+") as f:
            messages = pickle.load(f)
        logger.info("对话记录已加载。")
    else:
        logger.info("未找到保存的对话记录，初始化新对话。")


if __name__ == "__main__":
    read()
    print("开始对话（输入“结束对话”退出）：")

    while True:
        user_input = input("用户: ").strip()
        stop_tts()
        if user_input == "" or user_input == "结束对话":
            print("对话结束。")
            save()
            break
        print("AI:", end=' ', flush=True)

        ask(user_input)


