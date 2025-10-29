import datetime
import hashlib
import random
import time
from pathlib import Path

from fastapi import FastAPI, APIRouter
from loguru import logger
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

import api.eclock
import core.config
import core.convert
import core.ding_bot
import core.state
from ai import reader_agent

logger.add(
    "logs/log_{time}.log",  # 文件名可以带时间占位
    rotation = "10 MB",  # 文件超过 10 MB 自动切割
    retention = "10 days",  # 只保留 10 天
    compression = "zip",  # 旧文件压缩
    encoding = "utf-8",
    format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
)


def run():
    activity_diary_lists = api.eclock.get_activity_diary_lists()
    # 随机获取一条记录
    item = random.choice(activity_diary_lists)
    file_records = item.get('file_records')

    for file_record in file_records:
        file_record['duration'] = random.uniform(600, 800)
        file_record['audio_length'] = file_record['duration']
        file_record['size'] = random.uniform(3536078, 38936078)
        file_record['time'] = int(time.time())
        logger.info(f'file_record item: {file_record}')

    pdf_path = core.config.settings.pdf_file_path
    file_hash = hashlib.md5(str(Path(pdf_path).resolve()).encode('utf-8')).hexdigest()

    next_page = core.state.read_state().get(file_hash, {}).get("current_page", 1) + 1

    end_page = next_page + core.config.settings.pdf_limit
    book_info = core.convert.read_pdf(pdf_path, next_page, end_page)
    text_content = reader_agent.run(book_info)
    api.eclock.publish_daily(text_content, [file_records[0]])

    core.state.write_state({
        file_hash: {
            "current_page": end_page,
            "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    })

    media_info = f"""
    音频时长: {round(file_records[0].get('duration', 1) / 60, 2)}分
    音频大小: {round(file_records[0].get('size', 1) / (1024 * 1024), 2)}MB
    """
    core.ding_bot.send_ding_message(core.config.settings.ding.robot_webhook,
                                    f"成功打卡\n{text_content}\n {media_info}")


def main():
    try:
        run()
        return {
            "code": 200,
            "message": "打卡成功",
            "success": True
        }
    except Exception as e:
        logger.error(f"打卡失败: {str(e)}")
        # 出错时删除 Redis 中的 token
        redis_client = core.config.settings.get_redis_client()
        redis_client.delete('eclock_token')
        return {
            "code": 500,
            "message": f"打卡失败: {str(e)}",
            "success": False
        }


class TokenParams(BaseModel):
    token: str
    clock_in: bool = True


class RunParams(BaseModel):
    app_id: str
    activity_id: str
    clock_theme_id: str
    ai_api_key: str
    ding_webhook_url: str
    token: str

    def override(self):
        core.config.settings.app_id = self.app_id
        core.config.settings.activity_id = self.activity_id
        core.config.settings.clock_theme_id = self.clock_theme_id
        core.config.settings.ai.api_key = self.ai_api_key
        core.config.settings.ding.robot_webhook = self.ding_webhook_url
        if self.token:
            core.config.settings.token = self.token


# =========================
# FastAPI 实例
# =========================
app = FastAPI()
api_router = APIRouter(prefix = "/api/v1")

# =========================
# 中间件
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


@api_router.post("/clockIn")
def click_in(params: TokenParams):
    if params.token:
        redis_client = core.config.settings.get_redis_client()
        redis_client.set('eclock_token', params.token)
        logger.info(f"设置token: {params.token}")
    if params.click_in:
        return main()
    return "ok"


app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host = "0.0.0.0",
        port = 5001,
        workers = 20,
        reload = True  # 开发模式自动重载
    )
