import datetime
import hashlib
import random
import time
from pathlib import Path

from loguru import logger

import api.eclock
import core.config
import core.convert
import core.ding_bot
import core.state
from ai import reader_agent

logger.add(
    "logs/log_{time:YYYY-MM-DD}.log",  # 文件名按天生成
    rotation="00:00",                   # 每天零点切割
    retention="30 days",                 # 保留 10 天
    compression="zip",                   # 旧日志压缩
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}"
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
    except Exception as e:
        logger.error(e)
        core.ding_bot.send_ding_message(core.config.settings.ding.robot_webhook,
                                        f"失败打卡\n{e}")


if __name__ == "__main__":
    main()
