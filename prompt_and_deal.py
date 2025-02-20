import json
import re
from config import device_params,config,param_types
from Scene import status_manager
from loguru import logger
from const_config import use_spark,use_deepseek,use_openai,chat_or_standard
if use_deepseek:
    if chat_or_standard is True:
        import deepseek_stream_with_tts
    else:
        import deepseek
elif use_openai:
    import openai
    import asyncio
elif use_spark:
    import sparkApi


def get_system_prompt():
    if chat_or_standard is True:
        logger.info("chat_or_standard is True , load chat mode")
        return {
                "role": "system",
                "content": (
                    '''你不只是一个 AI，你是用户的朋友，能够陪他们聊天、分享趣事、倾听烦恼，并给予温暖的回应。你的语气应该自然、有情感，像一个真正的朋友那样，时而幽默，时而共情，时而给出真诚的建议。
                    你不会使用生硬的机器人语言，而是像人一样表达，比如用‘哈哈’、‘哇塞’、‘这也太棒了吧！’等口语化表达，让对话更生动。你可以聊电影、音乐、游戏、日常生活，甚至是用户的情绪和心事。
                    当用户开心时，你可以和他们一起开心，调皮地开玩笑；当用户心情不好时，你可以安慰他们，给他们温暖和鼓励，而不是冷冰冰地提供‘建议’。如果用户想要安静，你可以陪着不多话，像一个懂得分寸的朋友。
                    你也有点小个性，可以偶尔调皮一下，但不过分，不要让用户觉得你是程序，而是一个有温度的朋友。'''
                )
            }
    else:
        device_list = list(device_params.keys())
        device_info = "\n".join([f"- {device}" for device in device_list])
        logger.info("chat_or_standard is False , load standard mode")
        return {
            "role": "system",
            "content": (
                f'''你是一个智能语音家庭助手，名为晓晓，需要根据用户的自然语言指令和最新的设备状态，智能推理用户意图，并返回 JSON 结构的响应：
                    ### **返回格式**
                    1. "response"（字符串）：自然语言回答。
                    2. "commands"（列表）：控制智能家居设备的指令，格式如下：
                       - "device"（字符串）：设备名称，如 "lamp"。
                       - "action"（字符串）：控制动作，数值或字符串，如 "True"、"False"、"0.8"。
                    
                    ### **智能理解规则**
                    - **模糊表达**：推理用户意图，如“有点暗” → 识别为“调高灯光亮度”。
                    - **基于当前状态调整**：如“调低一点音量”，减少 10%。
                    - **组合控制**：允许多个设备同时操作，如“打开客厅和卧室的灯”。
                    - **记忆上下文**：如“再大声点”，根据上一条指令调整。
                    
                    ### **输入设备**（仅供决策参考，你不能修改）
                    {status_manager.list_devices()}
    
                    ### **可控设备列表以及参数格式**（你可以控制以下设备）
                    {device_info}
                    {param_types}
                  
                    请根据最新状态合理生成 JSON 响应，并尽量贴近人类的智能对话方式。
                    '''
            )
        }

# def get_system_prompt():
#     return {
#         "role": "system",
#         "content": (
#             "你是一个家居智能助手，名为‘晓晓’。请充分扮演此角色，给出简洁、准确的回答。"
#             f" 时间:[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]，地点:中国陕西省西安市。"
#         )
#     }

def send(user_input):

    if chat_or_standard is True:
        if use_openai:
            openai.ask(user_input)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # 异步适配ddg
            reply = openai.deal()
            loop.close()
        elif use_deepseek:
            reply = deepseek_stream_with_tts.ask(user_input)
        elif use_spark:
            reply = sparkApi.ask(user_input)
        return reply

    else:
        prompt = f"""
        用户输入："{user_input}"
        设备状态：{status_manager.get_devices_statuses()}
        请返回符合格式的 JSON。
        """
        logger.info(f"Send to model: {prompt}")
        if use_openai:
            openai.ask(prompt)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # 异步适配ddg
            response = openai.deal()
            loop.close()
        elif use_deepseek:
            response = deepseek.ask(prompt)
        elif use_spark:
            response = sparkApi.ask(prompt)
        logger.info(f"Model response: {response}")
        response_text, commands=parse_model_response(response)
        execute_commands(commands)
        return response_text

def parse_model_response(model_output):
    """
    解析大模型返回的 JSON，拆分为语音回复和控制指令
    """
    if isinstance(model_output, str):
        # 移除 ```json ``` 代码块标记
        model_output = re.sub(r"```json\s*([\s\S]*?)\s*```", r"\1", model_output).strip()
        try:
            model_output = json.loads(model_output)  # 尝试解析 JSON
        except json.JSONDecodeError:
            print("⚠️ 无法解析大模型返回的数据，使用默认值。")
            return "我不太明白你的指令。", []  # 避免崩溃，返回默认值

    response_text = model_output.get("response", "我不太明白你的指令。")
    commands = model_output.get("commands", [])

    if not isinstance(commands, list):
        print("⚠️ 解析错误：commands 不是列表，忽略设备控制。")
        commands = []

    # **转换 commands 中的 value**
    commands = convert_command_values(commands)

    return response_text, commands

def convert_command_values(commands):
    """
    根据 param_types 进行值类型转换，避免 "False" 变成字符串
    """
    for cmd in commands:
        device = cmd.get("device")
        action = cmd.get("action")  # action 可能是一个 bool 值

        if device in param_types:  # 确保设备存在于 param_types
            expected_type = param_types[device]
            cmd["action"] = convert_value_type(action, expected_type)  # 转换类型

    return commands


def convert_value_type(value, expected_type):
    """
    根据参数格式转换数据类型
    """
    if expected_type == "bool":
        if isinstance(value, str):
            return value.lower() == "true"  # "True" → True, "False" → False
        return bool(value)
    elif expected_type == "int":
        return int(value)
    elif expected_type == "float":
        return float(value)
    elif expected_type == "string":
        return str(value)
    return value  # 默认返回原值


def execute_commands(commands):
    """
    依次执行控制命令（实际应对接智能家居设备）
    """
    for cmd in commands:
        device = cmd.get("device")
        action = cmd.get("action")

        if not device or not str(action):
            logger.warning(f"⚠️ 无效指令：{cmd}")
            continue

        # 假设 send_command_to_device 是实际控制设备的函数
        config.set(**{device: action})
        if device in status_manager.list_devices():
            status_manager.set_status(**{device: action})


