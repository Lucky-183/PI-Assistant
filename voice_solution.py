from const_config import voice_solution,chat_or_standard

# 根据配置动态导入对应语音方案的三个核心模块：tts、reco、tts_stream
if voice_solution == "azure":
    # 导入azure方案的tts、reco、tts_stream
    from Azure_solution import tts, reco
    if chat_or_standard == True:
        from Azure_solution import tts_stream
        from Azure_solution.tts_stream import response_queue, tts_manager
elif voice_solution == "doubao":
    # 导入doubao方案的tts、reco、tts_stream
    from Doubao_solution import tts, reco
    if chat_or_standard == True:
        from Doubao_solution import tts_stream
        from Doubao_solution.tts_stream import response_queue, tts_manager
# else:
#     # 配置错误抛出明确异常，方便排查
#     raise ValueError(f"语音方案配置错误！仅支持azure/doubao，当前配置：{VOICE_SOLUTION}")
