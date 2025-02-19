import requests
import time
import os
import pickle
import json
from const_config import sfapikey
import threading
from queue import Queue
from loguru import logger
from tts_stream import TTSManager
from config import config

# DeepSeek API 配置
url = "https://api.siliconflow.cn/v1/chat/completions"
key = sfapikey  # 请替换为你的 DeepSeek API Key

# 全局对话记录，保存所有的对话消息（包括系统、用户和 AI 回复）
messages = []
response_queue = Queue()
tts_manager = TTSManager(response_queue)

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
            # "当用户输入为空或无意义时，请回复‘结束对话’。"
            f" 时间:[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]，地点:中国陕西省西安市。"
        )
    }
    messages.append(system_message)


def chat_request_stream():
    """
    调用 DeepSeek API 以流式方式获取 AI 回复，并解析 JSON 数据。
    """
    global messages
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Pro/deepseek-ai/DeepSeek-V3",
        "messages": messages,
        "stream": True,  # 启用流式返回
        "max_tokens": 512,
        "stop": ["null"],
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout = 30)
        if response.status_code == 200:
            ai_response = ""
            total_tokens = 0
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
                                if content.strip():
                                    response_queue.put(content)  # 发送给 TTS
                            if "usage" in json_data:
                                total_tokens = json_data["usage"].get("total_tokens", 0)
                        except json.JSONDecodeError:
                            continue
            response_queue.put("[END]")  # 标记对话结束
            # 将 AI 回复存入上下文
            messages.append({"role": "assistant", "content": ai_response})
            print('\n')
            # 监测 token 数，清理早期对话
            if len(messages) > 1 and total_tokens > 600:
                removed = messages.pop(1)  # 移除第一条非系统消息
                logger.warning(f"已移除历史记录: {removed}")
                if len(messages) > 1:
                    removed = messages.pop(1)  # 再移除一条非系统消息
                    logger.warning(f"已移除历史记录: {removed}")
            return ai_response
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"请求出错: {str(e)}")


def ask(user_input):
    """
    处理用户输入，更新对话记录，并使用流式方式返回 AI 回复。
    """
    global messages
    messages.append({"role": "user", "content": user_input})
    reply=chat_request_stream()
    return reply


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
        init_system()


tts_thread = threading.Thread(target=tts_manager.start_tts, daemon=True)
tts_thread.start()


if __name__ == "__main__":
    read()
    print("开始对话（输入“结束对话”退出）：")

    while True:
        user_input = input("用户: ").strip()
        tts_manager.stop_tts()
        if user_input == "" or user_input == "结束对话":
            print("对话结束。")
            save()
            break
        print("AI:", end=' ', flush=True)
        ask(user_input)
