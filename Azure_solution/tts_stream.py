import azure.cognitiveservices.speech as speechsdk
import threading
import pyaudio
from loguru import logger
from queue import Empty, Queue
import time
from const_config import azure_key

class TTSManager:
    def __init__(self, response_queue):
        """
        初始化 TTS 组件
        """
        self.stop_event = threading.Event()
        self.tts_task = None
        self.response_queue = response_queue

        # Azure TTS 配置
        self.speech_config = speechsdk.SpeechConfig(
            endpoint="wss://eastasia.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
            subscription=azure_key
        )
        self.speech_config.speech_synthesis_voice_name = "zh-CN-XiaoxiaoNeural"

        # 创建 TTS 输出流
        self.custom_callback = self.CustomPushStreamCallback(self)
        self.audio_output_stream = speechsdk.audio.PushAudioOutputStream(self.custom_callback)
        self.audio_config = speechsdk.audio.AudioOutputConfig(stream=self.audio_output_stream)

        self.speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=self.audio_config
        )

    class CustomPushStreamCallback(speechsdk.audio.PushAudioOutputStreamCallback):
        """
        自定义音频输出流回调
        """
        def __init__(self, tts_manager):
            super().__init__()
            self.tts_manager = tts_manager
            self.pyaudio_instance = pyaudio.PyAudio()
            self.stream = self.pyaudio_instance.open(format=pyaudio.paInt16,
                                                     channels=1,
                                                     rate=16000,
                                                     output=True,
                                                     frames_per_buffer=16384)

        def write(self, buffer: memoryview) -> int:
            """
            写入音频数据
            """
            if self.tts_manager.stop_event.is_set():
                logger.debug('Stopping audio')
                return 0
            self.stream.write(buffer.tobytes())
            return len(buffer)

        def close(self):
            """
            关闭音频流
            """
            self.stream.stop_stream()
            self.stream.close()
            self.pyaudio_instance.terminate()
            print("音频流已关闭。")

    def stop_tts(self):
        """
        停止当前 TTS 播放
        """
        logger.debug('Stopping TTS')
        self.speech_synthesizer.stop_speaking_async()
        self.stop_event.set()
        if self.tts_task:
            self.tts_task.get()
        self.stop_event.clear()

    def start_tts(self):
        """
        监听 response_queue，并使用流式方式朗读 AI 回复
        """
        logger.info('流式TTS启动')
        while True:
            # 🔍 **只检测队列是否有内容**
            if self.response_queue.empty():
                time.sleep(0.1)  # 避免高频空轮询，占用 CPU
                continue

            if self.stop_event.is_set():
                break

            # 🔄 **进入流式播放模式**
            tts_request = speechsdk.SpeechSynthesisRequest(
                input_type=speechsdk.SpeechSynthesisRequestInputType.TextStream
            )
            self.tts_task = self.speech_synthesizer.speak_async(tts_request)

            # **流式处理对话**
            while not self.stop_event.is_set():
                try:
                    text_chunk = self.response_queue.get(timeout=5)  # 等待新内容
                    if text_chunk == "[END]":
                        break  # **当前对话结束**
                    tts_request.input_stream.write(text_chunk)  # 🔥 **流式传输新文本**
                except Empty:
                    break  # **等待超时，结束当前对话**

            # 🔚 **关闭输入流，结束当前语音播放**
            tts_request.input_stream.close()

response_queue = Queue()
tts_manager = TTSManager(response_queue)
tts_thread = threading.Thread(target=tts_manager.start_tts, daemon=True)
tts_thread.start()