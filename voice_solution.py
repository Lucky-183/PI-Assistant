from const_config import voice_solution

# 根据配置动态导入对应语音方案的三个核心模块：tts、reco、tts_stream
if voice_solution == "azure":
    # 导入azure方案的tts、reco、tts_stream（保持原模块名，直接导入）
    from Azure_solution import tts, reco, tts_stream
    from Azure_solution.tts_stream import response_queue, tts_manager
# elif VOICE_SOLUTION == "doubao":
#     # 导入doubao方案的tts、reco、tts_stream（必须和azure同名，不一致则在__init__.py做别名）
#     from doubao import tts, reco, tts_stream
# else:
#     # 配置错误抛出明确异常，方便排查
#     raise ValueError(f"语音方案配置错误！仅支持azure/doubao，当前配置：{VOICE_SOLUTION}")
