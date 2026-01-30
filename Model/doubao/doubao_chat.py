import os
import pickle
from loguru import logger
from volcenginesdkarkruntime import Ark

# 从环境变量读取豆包API Key（建议配置到系统环境，也可直接赋值）
from const_config import ark_api_key  # 对齐你的配置方式，替换为你的ark_api_key

# 全局对话记录，保存所有的对话消息（包括系统、用户和AI回复）
messages = []

# 初始化豆包Ark客户端（全局单例）
client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=ark_api_key
)


def init_system():
    """
    初始化系统对话，添加系统提示（与原DeepSeek逻辑完全一致）
    """
    from prompt_and_deal import get_system_prompt
    global messages
    messages = []
    system_message = get_system_prompt()
    messages.append(system_message)
    logger.info("豆包对话系统已初始化，加载系统提示词")


def chat_request():
    """
    调用豆包火山方舟API接口，发送对话记录获取回复（替换原DeepSeek的requests调用）
    """
    try:
        # 调用豆包SDK的chat.completions.create，参数对齐原逻辑
        completion = client.chat.completions.create(
            model="doubao-seed-1-8-251228",  # 豆包模型ID，可根据需要修改
            messages=messages,
            stream=False,  # 非流式输出，与原逻辑一致
        )
        return completion  # 直接返回SDK结果对象，后续解析
    except Exception as e:
        # 异常格式与原逻辑一致，返回含error的字典
        logger.warning(f"豆包API调用异常: {str(e)}")
        return {"error": str(e)}


def ask(user_input):
    """
    处理用户输入，更新对话记录，调用API并返回回复（逻辑与原DeepSeek完全一致）
    """
    global messages
    # 添加用户输入到对话记录
    messages.append({"role": "user", "content": user_input.strip()})
    logger.info(f"接收用户输入，对话记录当前条数: {len(messages)}")

    # 调用豆包API
    result = chat_request()

    # 异常处理，与原逻辑一致
    if "error" in result:
        return f"豆包API请求错误: {result['error']}"

    # 解析豆包返回结果，适配SDK格式
    try:
        reply_message = result.choices[0].message
        # 提取思考内容（若有），豆包思考内容字段为thinking_content
        reasoning_response = getattr(reply_message, 'thinking_content', '')
        if reasoning_response:
            # print(f"豆包思考内容: {reasoning_response}")
            logger.info(f"豆包生成思考内容: {reasoning_response[:50]}...")

        # 将AI回复添加到对话记录
        messages.append({
            "role": reply_message.role,
            "content": reply_message.content.strip()
        })


        # 返回AI回复内容
        return reply_message.content.strip()
    except Exception as e:
        logger.warning(f"豆包结果解析异常: {str(e)}")
        return "未获取到豆包有效回复，请稍后重试。"


def save():
    """
    保存对话记录到本地message.data，与原逻辑完全一致
    """
    if os.path.exists('message.data'):
        os.remove('message.data')
    with open("message.data", 'wb+') as f:
        pickle.dump(messages, f)
    logger.info(f"豆包对话记录已保存，当前记录条数: {len(messages)}")


def read():
    """
    从本地加载对话记录，无记录则初始化系统，与原逻辑完全一致
    """
    global messages
    if os.path.exists('message.data'):
        with open('message.data', "rb+") as f:
            messages = pickle.load(f)
        logger.info(f"从本地加载对话记录成功，共{len(messages)}条")
    else:
        logger.info("未找到本地对话记录，初始化新对话")
        init_system()


# 测试主函数，与原DeepSeek代码完全一致
if __name__ == "__main__":
    # 加载历史记录（无则初始化）
    read()
    print("豆包对话已启动（输入“结束对话”退出）：")

    while True:
        user_input = input("用户: ").strip()
        if not user_input or user_input == "结束对话":
            print("对话结束，正在保存记录...")
            save()
            break

        # 调用对话接口并打印回复
        reply = ask(user_input)
        print("豆包:", reply)
        print("-" * 50)