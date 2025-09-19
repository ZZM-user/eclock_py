from loguru import logger

logger.add(
    "logs/log_{time:YYYY-MM-DD}.log",  # 文件名按天生成
    rotation="00:00",                   # 每天零点切割
    retention="30 days",                 # 保留 10 天
    compression="zip",                   # 旧日志压缩
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}"
)