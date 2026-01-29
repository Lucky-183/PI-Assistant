

import requests
import os
import pickle
from const_config import sfapikey
from loguru import logger


# DeepSeek API 配置
url = "https://api.siliconflow.cn/v1/chat/completions"
key = sfapikey  # 请替换为你的 DeepSeek API Key

# 全局对话记录，保存所有的对话消息（包括系统、用户和 AI 回复）
messages = []


def init_system():
    """
    初始化系统对话，添加系统提示（可根据需要进行调整）。
    """
    from prompt_and_deal import get_system_prompt
    global messages
    messages = []
    system_message = get_system_prompt()
    messages.append(system_message)


def chat_request():
    """
    调用 DeepSeek API 接口，发送当前的对话记录，获取回复。
    """
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Pro/deepseek-ai/DeepSeek-V3",
        "messages": messages,
        "stream": False,
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
        response = requests.post(url, headers = headers, json = payload)
        result = response.json()
    except Exception as e:
        result = {"error": str(e)}
    return result


def ask(user_input):
    """
    处理用户输入，更新对话记录，并返回 AI 回复内容。
    """
    global messages
    # 添加用户输入
    messages.append({"role": "user", "content": user_input})

    result = chat_request()

    if "error" in result:
        return f"请求错误: {result['error']}"

    # 检查返回结果是否正确（假设返回结构与 OpenAI 类似）
    if "choices" in result and len(result["choices"]) > 0:
        reply_message = result["choices"][0].get("message")
        if reply_message is None:
            return "没有获取到有效的回复。"
        reasoning_response=reply_message.get('reasoning_content', '')
        if reasoning_response:
            print(f"reasoning_content:{reasoning_response}")
        messages.append({
            "role": reply_message.get("role", ""),
            "content": reply_message.get("content", "")
        })
        if len(messages) > 1 and result['usage']['total_tokens'] > 600:
            removed = messages.pop(1)  # 移除第一条非系统消息
            logger.warning("已移除历史记录:", removed)
            removed = messages.pop(1)  # 移除第一条非系统消息
            logger.warning("已移除历史记录:", removed)
        return reply_message.get("content", "")
    else:
        return "未收到有效回复，请稍后重试。"


def save():
    """
    将当前对话记录保存到本地文件，方便后续加载。
    """
    if(os.path.exists('message.data')):
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


if __name__ == "__main__":
    # 初始化对话（也可以调用 load_conversation() 加载之前的对话记录）
    #init_system()
    read()
    print("开始对话（输入“结束对话”退出）：")

    while True:
        user_input = input("用户: ").strip()
        if user_input == "" or user_input == "结束对话":
            print("对话结束。")
            save()
            break

        reply = ask(user_input)
        print("AI:", reply)
