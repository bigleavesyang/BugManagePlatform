FROM python:3.12-slim-bullseye
# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DB_PASSWORD="123456"

# 配置apt使用阿里云镜像源
RUN echo "deb http://mirrors.aliyun.com/debian/ bullseye main non-free contrib" > /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian-security/ bullseye-security main" >> /etc/apt/sources.list

# 安装系统依赖
RUN apt update \
    && apt install -y --no-install-recommends \
    gcc \
    python3-dev \
    pkg-config \
    libmariadb-dev-compat \
    build-essential \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*


# 配置pip使用阿里云源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set install.trusted-host mirrors.aliyun.com

# 创建uwsgi日志目录
RUN mkdir -p /var/log/uwsgi

# 复制项目依赖文件
COPY requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install uwsgi

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8080

# 创建启动脚本
RUN echo '#!/bin/bash\n\
# 等待数据库服务就绪\n\
while ! nc -z mysql 3306; do\n\
  echo "Waiting for MySQL to be ready..."\n\
  sleep 1\n\
done\n\
\n\
# 等待Redis服务就绪\n\
while ! nc -z redis 6379; do\n\
  echo "Waiting for Redis to be ready..."\n\
  sleep 1\n\
done\n\
\n\
# 执行数据库迁移\n\
python manage.py migrate --noinput\n\
\n\
# 收集静态资源\n\
python manage.py collectstatic --noinput\n\
\n\
# 启动uwsgi\n\
uwsgi --ini uwsgi.ini\n\
\n\
# 保持容器运行并监控uwsgi日志\n\
tail -f /var/log/uwsgi/uwsgi.log' > /app/start.sh

# 给启动脚本添加执行权限
RUN chmod +x /app/start.sh

# 使用启动脚本作为入口点
CMD ["/app/start.sh"]