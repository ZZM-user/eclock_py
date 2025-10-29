# 基础镜像
FROM astral/uv:python3.12-alpine

# 设置工作目录
WORKDIR /app

# 复制应用源码
COPY . /app

# 安装依赖
RUN uv sync

# 暴露端口
EXPOSE 5001

# 启动命令
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
