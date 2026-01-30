# coding=utf-8
#参考https://www.volcengine.com/docs/6561/1354869?lang=zh
import uuid
import base64
import requests
from const_config import doubao_appid,doubao_access_token
from loguru import logger

url = "https://openspeech.bytedance.com/api/v1/tts"

def wav(text: str, filename: str):
    appid = doubao_appid
    access_token = doubao_access_token
    VOICE_TYPE = "zh_female_cancan_mars_bigtts"

    headers = {
        "Authorization": f"Bearer;{access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "app": {
            "appid": appid,
            "token": access_token,
            "cluster": "volcano_tts",
        },
        "user": {
            "uid": str(uuid.uuid4()),
        },
        "audio": {
            "voice_type": VOICE_TYPE,
            "encoding": "mp3",
            "sample_rate": 24000,
            "bitrate": 128000,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "text_type": "plain",
            "operation": "query",
        },
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    result = resp.json()

    if result.get("code") != 3000:
        raise RuntimeError(result)

    data = result.get("data")

    # ✅ 关键修复点：兼容两种返回
    if isinstance(data, dict):
        audio_b64 = data.get("audio")
    elif isinstance(data, str):
        audio_b64 = data
    else:
        raise RuntimeError(f"Unexpected data type: {type(data)}")

    if not audio_b64:
        raise RuntimeError("Empty audio data")

    audio_bytes = base64.b64decode(audio_b64)

    with open(filename, "wb") as f:
        f.write(audio_bytes)
    logger.info("豆包TTS：音频合成结束")

if __name__ == "__main__":
    wav("夜深了，祝您晚安", "goodnight.wav")
