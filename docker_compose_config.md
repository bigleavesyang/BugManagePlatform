# services1主项目
BugManagePlatform镜像依赖于python解释器，mysql,redis。对外暴露8080端口。加入bug_manage_platform_network网络。

# services2 python
python解释器镜像。

# services3 mysql
mysql镜像。加入bug_manage_platform_network网络。
# !!!!!!!!!!!!!!!!! 注意同行的配置中间有“空格”，不然报错。
name: mysql
services:
  mysql:
    container_name: mysql
    image: bitnami/mysql:latest
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=123456
    volumes:
      - /root/bug_manage_platform/mysql:/bitnami/mysql/data \
    networks:
      - bug_manage_platform_network
    restart: always

# services4 redis
redis镜像。加入bug_manage_platform_network网络。
name: redis
services:
  redis01:
    container_name: redis
    image: bitnami/redis:latest
    ports:
      - "6379:6379"
    environment:
      - REDIS_PASSWORD=123456
    volumes:
      - /root/bug_manage_platform/redis:/bitnami/redis/data
    networks:
      - bug_manage_platform_network
    restart: always

networks:
  bug_manage_platform_network:
    driver: bridge
