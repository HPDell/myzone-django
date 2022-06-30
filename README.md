# MyZone: a personal blog web application.

[![Docker Image CI](https://github.com/HPDell/myzone-django/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/HPDell/myzone-django/actions/workflows/docker-publish.yml)

[Example](https://blog.huyg.site:8443/) | [中文说明](./README_CN.md)

![](https://hpdell.github.io/assets/cover/dynamic-blog-v2.png)

This is a [Django](https://www.djangoproject.com/), [Bootstrap](https://getbootstrap.com/) and [Vditor](https://github.com/Vanessa219/vditor) based personal blog application.
Both English and Chinese pages are avaliable.
This blog includes these modules:

- Home page
- Blogs
- Publications

For blogs, it support online create, read, update and delete.
But only users authorized as staff are permitted to do these dangerous actions.
Please manage users, groups and all entities in the Django Admin site.

If you are familiar with django, it will be very easy to add some extensions like album.

## Deployment

[Docker image](https://hub.docker.com/r/hpdell/myzone-django) is recommanded and the following Docker Compose file is suggested to deploy MyZone.
If you are using Docker image, there is no need to manually add a super user.

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
      DJANGO_SUPERUSER_USERNAME: admin
      DJANGO_SUPERUSER_EMAIL: admin@example.com
      DJANGO_SUPERUSER_PASSWORD: myzonepassword
      DJANGO_DATABASE_USER: admin
      DJANGO_DATABASE_PASSWORD: myzonepassword
      DJANGO_DATABASE_NAME: myzone
      MYZONE_HOST: example.com

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

Note that some environment variables need to be matched:

- `DJANGO_DATABASE_USER` = `POSTGRES_USER`
- `DJANGO_DATABASE_PASSWORD` = `POSTGRES_DB`
- `DJANGO_DATABASE_NAME` = `POSTGRES_PASSWORD`

If you don't want to use docker, it is also possible to start this application
by `python` like this

```bash
python manage.py migrate
python manage.py createsuperuser --no-input
python manage.py collectstatic
python manage.py compilemessages
python manage.py runserver 0.0.0.0:8000
```
