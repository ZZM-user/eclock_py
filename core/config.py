import sys
from pathlib import Path

import redis
import tomli
from core.log import logger
from pydantic_settings import BaseSettings

__all__ = ["settings"]


class Ai(BaseSettings):
    api_key: str
    base_url: str
    model_id: str
    prompt: str


class Ding(BaseSettings):
    robot_webhook: str


class Config(BaseSettings):
    token: str
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    app_id: str = 'appVH4ImDNo1647'
    activity_id: str
    clock_theme_id: str = ""
    pdf_file_path: str
    pdf_limit: int = 5
    ai: Ai
    ding: Ding

    @classmethod
    def from_toml(cls, filename: str = "settings.toml") -> "Config":
        """
        依次查找：
        1. 项目根目录（源码运行时）
        2. 可执行文件同级目录（PyInstaller/Frozen exe）
        3. 包内默认位置
        """
        # 1. exe 同级目录（打包后 sys.executable 指向 exe）
        exe_path = Path(sys.executable).resolve().parent / filename
        logger.info(f"从 {exe_path} 加载配置文件")
        if exe_path.exists():
            return cls(**tomli.loads(exe_path.read_text(encoding = "utf-8")))

        # 2. 项目根目录
        root_path = Path.cwd() / filename
        logger.info(f"从 {root_path} 加载配置文件")
        if root_path.exists():
            return cls(**tomli.loads(root_path.read_text(encoding = "utf-8")))

        # 3. 包内默认文件（可选，如果你在包里放了一个默认 settings.toml）
        pkg_default = Path(__file__).with_name(filename)
        logger.info(f"从 {pkg_default} 加载配置文件")
        if pkg_default.exists():
            return cls(**tomli.loads(pkg_default.read_text(encoding = "utf-8")))

        raise FileNotFoundError(f"无法找到配置文件 {filename}")

    def get_redis_client(self) -> redis.Redis:
        """
        获取 Redis 客户端实例
        :return: Redis 客户端
        """
        return redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            decode_responses=True
        )


settings = Config.from_toml()
