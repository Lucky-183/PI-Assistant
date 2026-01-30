import os
import pickle
import threading
from queue import Queue
from loguru import logger
from volcenginesdkarkruntime import Ark
from voice_solution import response_queue
from const_config import doubao_api_key

# 初始化豆包Ark客户端（全局单例，流式专用）
client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=doubao_api_key
)

messages = []

def init_system():
    """初始化系统对话，添加系统提示词，与原代码逻辑完全一致"""
    from prompt_and_deal import get_system_prompt
    global messages
    messages = []
    system_message = get_system_prompt()
    messages.append(system_message)
    logger.info("豆包流式对话：系统提示词初始化完成")


def chat_request_stream():
    """
    核心：调用豆包SDK流式接口，解析content和reasoning_content，推流到TTS队列
    完全对齐原DeepSeek流式逻辑，仅替换底层API调用和解析方式
    """
    global messages
    ai_response = ""  # 拼接完整AI回复
    reasoning_response = ""  # 拼接完整思考内容
    total_tokens = 0  # 记录总令牌数，用于后续裁剪

    try:
        # 调用豆包流式接口，参数对齐原代码的配置
        completion = client.chat.completions.create(
            model="doubao-seed-1-8-251228",  # 豆包模型ID，可根据需要修改
            messages=messages,
            stream=True,  # 非流式输出，与原逻辑一致
        )

        # with语句确保连接自动关闭，避免泄露（豆包官方推荐）
        with completion:
            for chunk in completion:
                # 跳过空chunk，防止解析异常
                if not chunk or not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                # 解析思考内容（reasoning_content），对齐豆包返回格式
                reasoning_content = getattr(delta, 'reasoning_content', '') or ""
                # 解析回复内容（content）
                content = getattr(delta, 'content', '') or ""

                # 拼接思考内容并实时打印，和原代码一致
                if reasoning_content:
                    reasoning_response += reasoning_content
                    print(reasoning_content, end='', flush=True)
                # 拼接回复内容、实时打印、推流到TTS队列
                if content:
                    ai_response += content
                    print(content, end='', flush=True)  # 控制台流式输出
                    response_queue.put(content)  # 推给TTS实时播放，核心逻辑
        #
        # 流式结束：添加[END]标记，通知TTS停止播放（和原代码完全一致）
        response_queue.put("[END]")
        logger.info(f"豆包流式推流完成，总回复长度：{len(ai_response)}，思考内容长度：{len(reasoning_response)}")

        # 提取令牌数（豆包流式最后会返回usage，兼容原裁剪逻辑）
        if hasattr(completion, 'usage') and completion.usage:
            total_tokens = completion.usage.get('total_tokens', 0)

        # 将完整AI回复存入对话历史，和原代码一致
        messages.append({"role": "assistant", "content": ai_response})
        print('\n')  # 流式结束后换行，优化控制台显示

        # 令牌数超限，裁剪早期非系统历史记录（和原代码的裁剪规则完全一致）
        if len(messages) > 1 and total_tokens > 600:
            removed = messages.pop(1)
            logger.warning(f"豆包流式对话：令牌超限，移除历史记录：{removed['content'][:50]}...")
            if len(messages) > 1:
                removed = messages.pop(1)
                logger.warning(f"豆包流式对话：令牌超限，再移除一条历史记录：{removed['content'][:50]}...")

        return ai_response

    except Exception as e:
        # 异常处理，和原代码的提示风格一致
        err_msg = f"豆包流式API调用出错: {str(e)}"
        print(err_msg)
        logger.error(err_msg)
        # response_queue.put("[END]")  # 异常也标记TTS结束，避免阻塞
        return ""


def ask(user_input):
    """处理用户输入，更新对话记录，调用流式接口，与原代码逻辑完全一致"""
    global messages
    # 过滤空输入，添加用户消息到历史
    user_input = user_input.strip()
    if not user_input:
        return ""
    messages.append({"role": "user", "content": user_input})
    logger.info(f"豆包流式对话：接收用户输入 -> {user_input[:30]}...")
    # 调用流式接口，返回完整回复
    reply = chat_request_stream()
    return reply


def save():
    """保存对话记录到本地message.data，与原代码完全一致"""
    if os.path.exists('message.data'):
        os.remove('message.data')
    with open("message.data", 'wb+') as f:
        pickle.dump(messages, f)
    logger.info("豆包流式对话：本地对话记录保存完成")


def read():
    """从本地加载对话记录，无记录则初始化系统，与原代码完全一致"""
    global messages
    if os.path.exists('message.data'):
        with open('message.data', "rb+") as f:
            messages = pickle.load(f)
        logger.info(f"豆包流式对话：从本地加载对话记录，共{len(messages)}条")
    else:
        logger.info("豆包流式对话：未找到本地记录，初始化新对话")
        init_system()



# 主函数：交互入口，和原DeepSeek流式代码完全一致，无缝替换
if __name__ == "__main__":
    # 加载历史记录/初始化系统
    read()
    print("豆包流式对话已启动（输入“结束对话”退出）：")

    while True:
        user_input = input("用户: ").strip()
        # 每次新输入先停止上一次TTS，避免音频重叠
        # tts_manager.stop_tts()
        # 退出条件，和原代码一致
        if not user_input or user_input == "结束对话":
            print("对话结束，正在保存记录...")
            save()
            break
        # 流式输出AI回复，和原代码的打印格式一致
        print("AI:", end=' ', flush=True)
        # 调用流式对话接口
        ask(user_input)