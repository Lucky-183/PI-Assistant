#参考https://www.volcengine.com/docs/6561/1631584?lang=zh
import uuid
import base64
import requests
import json
from const_config import doubao_appid,doubao_access_token
from loguru import logger


# 辅助函数：将本地文件转换为Base64
def file_to_base64(file_path):
    with open(file_path, 'rb') as file:
        file_data = file.read()  # 读取文件内容
        base64_data = base64.b64encode(file_data).decode('utf-8')  # Base64 编码
    return base64_data


# recognize_task 函数
def recognize(file_path='Sound/question.wav'):
    recognize_url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"
    # 填入控制台获取的app id和access token
    appid = doubao_appid
    token = doubao_access_token

    headers = {
        "X-Api-App-Key": appid,
        "X-Api-Access-Key": token,
        "X-Api-Resource-Id": "volc.bigasr.auc_turbo",
        "X-Api-Request-Id": str(uuid.uuid4()),
        "X-Api-Sequence": "-1",
    }

    # 检查是使用文件URL还是直接上传数据
    audio_data = None

    base64_data = file_to_base64(file_path)  # 转换文件为 Base64
    audio_data = {"data": base64_data}  # 使用Base64编码后的数据

    if not audio_data:
        raise ValueError("必须提供 file_url 或 file_path 其中之一")

    request = {
        "user": {
            "uid": appid
        },
        "audio": audio_data,
        "request": {
            "model_name": "bigmodel",
            # "enable_itn": True,
            # "enable_punc": True,
            # "enable_ddc": True,
            # "enable_speaker_info": False,

        },
    }

    response = requests.post(recognize_url, json=request, headers=headers)
    if 'X-Api-Status-Code' in response.headers:
        logger.debug(f'recognize task Status-Code is: {response.headers["X-Api-Status-Code"]} ')
        content = json.loads(response.text)
        logger.info(f'{content["result"]["text"]}')
        return content["result"]["text"]
    else:
        logger.warning(f'recognize task failed and the response headers are:: {response.headers}\n')
        return None



if __name__ == '__main__':
    recognize()