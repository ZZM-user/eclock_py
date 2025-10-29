import requests
from core.log import logger

import core.config
from core.config import settings

__HOST = 'https://eclock.h5.xiaoeknow.com'


def _get_token():
    """
    从 Redis 获取 token，如果不存在则使用配置中的 token
    :return: token
    """
    redis_client = settings.get_redis_client()
    token = redis_client.get('eclock_token')
    if not token:
        token = settings.token
        redis_client.set('eclock_token', token)
    return token


def get_user_id() -> str:
    """
    获取用户ID
    :return:
    """
    config = core.config.settings
    url = f'{__HOST}/eclock/get_user_id'

    headers = {'Cookie': f'token={_get_token()}'}

    body = {"app_id": config.app_id}

    response = requests.post(url, headers = headers, json = body)
    logger.info(f'获取userId：{response.json()}')
    return response.json().get('data').get('user_id')


def get_activity_diary_lists(page_index: int = 1, page_size: int = 20) -> list[dict]:
    """
    获取打卡列表
    :param page_index: 页码
    :param page_size: 每页数量
    :return:
    """
    config = core.config.settings
    url = f'{__HOST}/punch_card/activity_diary_lists/2.0.0'

    headers = {'Cookie': f'token={_get_token()}'}

    body = {
        "app_id": config.app_id,
        "activity_id": config.activity_id,
        "src_user_id": get_user_id(),
        "page_index": page_index,
        "page_size": page_size
    }

    response = requests.post(url, headers = headers, json = body)
    logger.info(f'获取结果：{response.json()}')
    return response.json().get('data').get('list')


def publish_daily(text_content: str, file_records: list[dict]):
    """
    发表日记
    :param text_content: 文字内容
    :param file_records: 文件内容（音频）
    :return:
    """
    config = core.config.settings

    url = f'{__HOST}/punch_card/publish_diary/2.0.0'

    headers = {'Cookie': f'token={_get_token()}'}

    body = {
        "clock_theme_id": config.clock_theme_id,
        "activity_id": config.activity_id,
        "text_content": text_content,
        "content_type": 0,
        "is_private": 0,
        "app_id": config.app_id,
        "img_urls": [],
        "audio_records": [],
        "video_records": [],
        "mix_records": [],
        "file_records": file_records
    }

    response = requests.post(url, headers = headers, json = body)
    logger.info(f'发布结果：{response.json()}')

    # 返回不含 打卡成功 就是失败，需要断言
    if "打卡成功" not in str(response.json()):
        # 打卡失败，删除 Redis 中的 token
        redis_client = settings.get_redis_client()
        redis_client.delete('eclock_token')
        raise RuntimeError(f"打卡失败！接口返回结果为：{response.json()}")


def get_user_info() -> dict:
    """
    获取用户信息
    :return:
    """
    config = core.config.settings
    url = f'{__HOST}/eclock/get_user_info'

    headers = {'Cookie': f'token={config.token}'}

    response = requests.post(url, headers = headers)
    logger.info(f'获取用户信息：{response.json()}')
    return response.json().get('data')

def get_user_join_clock():
    """
    获取用户参与打卡列表
    :return:
    """
    config = core.config.settings
    url = f'{__HOST}/eclock/user_join_clock/2.0.0'

    headers = {'Cookie': f'token={config.token}'}
    body = {"page_index":1,"page_size":10}

    response = requests.post(url, headers = headers, json = body)
    logger.info(f'获取用户参与打卡列表：{response.json()}')
    return response.json().get('data')