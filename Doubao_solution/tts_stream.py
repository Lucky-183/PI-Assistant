#参考https://www.volcengine.com/docs/6561/1354869?lang=zh
import asyncio
import threading
import uuid
import json
import time
import pyaudio
import websockets
from queue import Empty, Queue
from loguru import logger
from const_config import doubao_appid,doubao_access_token

from Doubao_solution.protocols import (
    EventType,
    MsgType,
    start_connection,
    finish_connection,
    start_session,
    finish_session,
    task_request,
    receive_message,
    wait_for_event,
    cancel_session  # 导入取消会话的异步函数
)

class TTSTask:
    """极简版 TTS 播放状态任务"""
    def __init__(self):
        self._finished = False

    def mark_finished(self):
        """调用此方法表示播放完成或被打断"""
        self._finished = True

    def doing(self):
        """调用此方法表示播放完成或被打断"""
        self._finished = False

    def get(self) -> bool:
        """获取播放状态"""
        return self._finished


class TTSManager:
    """
    豆包流式TTS管理器（支持打断重放、WS长连接）
    使用方式与 Azure TTSManager 完全一致
    """
    @staticmethod
    def get_resource_id(voice: str) -> str:
        if voice.startswith("S_"):
            return "volc.megatts.default"
        return "volc.service_type.10029"

    def __init__(
        self,
        response_queue,
        voice_type="zh_female_cancan_mars_bigtts",
        resource_id="",
    ):
        self.response_queue = response_queue
        self.interrupt_event = threading.Event()  # 打断标志位（替代原stop_event）
        self.current_session_id = None  # 记录当前正在执行的会话ID，用于取消
        self.ws = None  # 保存WS长连接对象，全程复用
        self.tts_task = TTSTask()

        # 豆包配置
        self.APP_ID = doubao_appid
        self.ACCESS_TOKEN = doubao_access_token
        self.VOICE_TYPE = voice_type
        self.RESOURCE_ID = resource_id if resource_id else self.get_resource_id(voice_type)
        self.endpoint = "wss://openspeech.bytedance.com/api/v3/tts/bidirection"

        # 音频播放配置
        self.pyaudio = pyaudio.PyAudio()
        self.audio_stream = self.pyaudio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,
            output=True,
            frames_per_buffer=4096,
        )
        self.audio_stream.start_stream()

    def start_tts(self):
        """启动TTS：建立WS长连接，持续监听队列并处理TTS请求（支持打断）"""
        logger.info("豆包流式TTS：服务启动，开始建立WS长连接")
        self.interrupt_event.clear()
        threading.Thread(target=self._run_loop, daemon=True).start()

    def stop_tts(self):
        """
        核心打断方法：清空队列+触发中断+取消当前会话+重置标志位
        调用后可立即推入新文本，重新开始TTS
        """
        logger.debug('豆包流式TTS：接收打断指令，停止当前播放')
        if self.interrupt_event.is_set():
            return  # 避免重复打断
        # 1. 触发中断标志
        self.interrupt_event.set()
        # 2. 清空队列，避免残留文本干扰新会话
        with self.response_queue.mutex:
            self.response_queue.queue.clear()
        logger.info("豆包流式TTS：队列已清空，等待当前会话取消")

    def _run_loop(self):
        """线程内运行的asyncio循环入口"""
        asyncio.run(self._tts_main_loop())

    async def _tts_main_loop(self):
        """WS长连接主循环：连接建立后持续复用，直到进程退出"""
            # 建立WS长连接，全程只创建一次
        headers = {
            "X-Api-App-Key": self.APP_ID,
            "X-Api-Access-Key": self.ACCESS_TOKEN,
            "X-Api-Resource-Id": self.RESOURCE_ID,
            "X-Api-Connect-Id": str(uuid.uuid4()),
        }
        async with websockets.connect(
            self.endpoint,
            extra_headers=headers,
            max_size=10 * 1024 * 1024,
        ) as self.ws:
            # 初始化连接握手
            await start_connection(self.ws)
            await wait_for_event(self.ws, MsgType.FullServerResponse, EventType.ConnectionStarted)
            # logger.info("豆包流式TTS：WebSocket连接建立")

            # 持续监听队列，处理TTS请求（串行执行，支持打断）
            while True:
                # 检测队列是否有内容，无内容则低频率轮询，减少CPU占用
                if self.response_queue.empty():
                    await asyncio.sleep(0.1)
                    continue
                self.interrupt_event.clear()
                await self._handle_single_tts_session()
                logger.info("豆包流式TTS：当前会话执行完成")

    async def _handle_single_tts_session(self):
        self.current_session_id = str(uuid.uuid4())
        session_id = self.current_session_id
        logger.info(f"豆包流式TTS：启动新会话，ID={session_id[:8]}")

        # 步骤1：启动当前会话
        try:
            req = {
                "event": EventType.StartSession,
                "user": {"uid": str(uuid.uuid4())},
                "namespace": "BidirectionalTTS",
                "req_params": {
                    "speaker": self.VOICE_TYPE,
                    "audio_params": {"format": "pcm", "sample_rate": 24000},
                },
            }
            self.tts_task.doing()
            await start_session(self.ws, json.dumps(req).encode(), session_id)
            await wait_for_event(self.ws, MsgType.FullServerResponse, EventType.SessionStarted)
        except Exception as e:
            logger.warning(f"豆包流式TTS：会话{session_id[:8]}启动失败 - {str(e)}")
            self.current_session_id = None
            return

        # 步骤2：创建发送文本、接收音频的异步任务
        send_task = asyncio.create_task(self._send_text_stream(session_id))
        recv_task = asyncio.create_task(self._recv_audio_stream(session_id))

        # 步骤3：等待任务完成（被打断/文本发送完毕/3秒超时）
        await asyncio.gather(send_task, recv_task, return_exceptions=True)

        # # 步骤4：会话收尾：无论是否正常结束，都尝试取消/结束会话，重置状态

        if self.interrupt_event.is_set():
            await cancel_session(self.ws, session_id)  # 打断时主动取消会话
            await wait_for_event(self.ws, MsgType.FullServerResponse, [EventType.SessionCanceled,EventType.SessionFinished])
            self.tts_task.mark_finished()
            logger.info(f"豆包流式TTS：会话{session_id[:8]}已被取消")



    async def _send_text_stream(self, session_id):
        """流式发送文本：响应打断信号"""
        while not self.interrupt_event.is_set():
                # 3秒超时：队列无新文本则结束发送，实现文本聚合
            text_chunk = self.response_queue.get(timeout=3)
            if text_chunk == "[END]":
                # logger.info(f"豆包流式TTS：会话{session_id[:8]}收到结束标志，停止文本发送")
                await finish_session(self.ws, session_id)  # 正常结束时完成会话
                break
            # 逐段发送文本（保持原逻辑，轻微延时避免服务端压力）
            req = {"event": EventType.TaskRequest, "req_params": {"text": text_chunk}}
            await task_request(self.ws, json.dumps(req).encode(), session_id)
            await asyncio.sleep(0.003)

    async def _recv_audio_stream(self, session_id):
        """流式接收音频并播放：响应打断信号，会话结束则退出"""
        while not self.interrupt_event.is_set():
            msg = await receive_message(self.ws)
            # 音频数据：写入播放流
            if msg.type == MsgType.AudioOnlyServer:
                data = msg.payload.tobytes() if hasattr(msg.payload, "tobytes") else bytes(msg.payload)
                self.audio_stream.write(data)
            # 会话结束标志：退出接收
            elif msg.type == MsgType.FullServerResponse and msg.event == EventType.SessionFinished:
                self.tts_task.mark_finished()
                break

response_queue = Queue()
tts_manager = TTSManager(response_queue)
tts_thread = threading.Thread(target=tts_manager.start_tts, daemon=True)
tts_thread.start()
logger.info("豆包流式TTS管理器线程已启动")




# 测试/使用示例
if __name__ == "__main__":

    response_queue.put("你好我是豆包流式TTS")
    response_queue.put("支持实时打断重放。")
    response_queue.put("[END]")