import json

import requests
from loguru import logger


def send_ding_message(webhook: str, message: str) -> None:
    if not webhook:
        return

    message = f'{message}\n【鹅打卡推送】\n'

    headers = {"Content-Type": "application/json"}
    payload = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    response = requests.post(webhook, headers = headers, data = json.dumps(payload))
    if response.status_code == 200:
        logger.info(f"【ding WebHook】发送成功:{response.json()}")
    else:
        logger.info(f"【ding WebHook】发送失败:{response.status_code}{response.text}")
