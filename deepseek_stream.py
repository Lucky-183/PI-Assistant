import requests
import time
import json
import threading
from queue import Queue
from loguru import logger
from const_config import sfapikey
from tts_stream import TTSManager

# DeepSeek API 配置
url = "https://api.siliconflow.cn/v1/chat/completions"
key = sfapikey  # 请替换为你的 DeepSeek API Key

# 对话上下文
messages = []
response_queue = Queue()
tts_manager = TTSManager(response_queue)

def init_system():
    """
    初始化对话，添加系统提示
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
    调用 DeepSeek API 并将 AI 响应逐步传递到 response_queue
    """
    global messages
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Pro/deepseek-ai/DeepSeek-V3",
        "messages": messages,
        "stream": True,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"}
    }

    response = requests.post(url, headers=headers, json=payload, stream=True)
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
        messages.append({"role": "assistant", "content": ai_response})

        if total_tokens > 600:
            messages.pop(1)  # 移除旧的对话
    else:
        print(f"请求失败，状态码: {response.status_code}")

def ask(user_input):
    """
    处理用户输入，更新对话记录，并使用流式方式返回 AI 回复
    """
    global messages
    messages.append({"role": "user", "content": user_input})
    chat_request_stream()

if __name__ == "__main__":
    init_system()
    tts_thread = threading.Thread(target=tts_manager.start_tts, daemon=True)
    tts_thread.start()

    while True:
        user_input = input("用户: ").strip()
        tts_manager.stop_tts()
        if user_input == "" or user_input == "结束对话":
            print("对话结束。")
            break
        print("AI:", end=' ', flush=True)
        ask(user_input)
