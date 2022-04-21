# MyZone：个人博客应用

[![Docker Image CI](https://github.com/HPDell/myzone-django/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/HPDell/myzone-django/actions/workflows/docker-publish.yml)

[示例](https://blog.huyg.site:8443/) | [英文说明](./README.md)

![](https://hpdell.github.io/assets/cover/dynamic-blog-v2.png)

这是一个基于 [Django](https://www.djangoproject.com/), [Bootstrap](https://getbootstrap.com/) 和 [Vditor](https://github.com/Vanessa219/vditor) 的个人博客应用。
支持英语和简体中文两种语言。
包括以下模块：

- 主页
- 博客
- 发表成果

对于博客模块，该应用支持在线创建、阅读、编辑和删除。
但只有认证具有 staff 权限的用户才能执行这些操作。
请在 Django Admin 页面中管理用户、用户组以及其他所有实体。

如果你熟悉 Django 框架，那么可以很容易添加一些扩展，例如相册。

## 部署

推荐使用 [Docker image](https://hub.docker.com/r/hpdell/myzone-django) 并安装下面所示的 Docker Compose 配置文件来部署 MyZone。
如果你使用这种方式，就无需手动创建超级用户。

```yml
version: '3.8'

services:
  app:
    build: .
    volumes:
      - upload-data:/code/uploads
    ports:
      - "8080:8000"
    depends_on:
      - db
    links:
      - "db:db"
    restart: unless-stopped
    environment:
      - DJANGO_SUPERUSER_USERNAME=admin
      - DJANGO_SUPERUSER_EMAIL=admin@example.com
      - DJANGO_SUPERUSER_PASSWORD=myzonepassword
      - DJANGO_DATABASE_USER=admin
      - DJANGO_DATABASE_PASSWORD=myzonepassword
      - DJANGO_DATABASE_NAME=myzone

  db:
    image: postgres:latest
    restart: unless-stopped
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: admin
      POSTGRES_DB: myzone
      POSTGRES_PASSWORD: myzonepassword

volumes:
  postgres-data: null
  upload-data: null
```

注意有些环境变量需要能够匹配：

- `DJANGO_DATABASE_USER` = `POSTGRES_USER`
- `DJANGO_DATABASE_PASSWORD` = `POSTGRES_DB`
- `DJANGO_DATABASE_NAME` = `POSTGRES_PASSWORD`

如果你不想使用 Docker，也可以使用 `python` 命令按照如下方式启动该应用：

```bash
python manage.py migrate
python manage.py createsuperuser --no-input
python manage.py collectstatic
python manage.py compilemessages
python manage.py runserver 0.0.0.0:8000
```
